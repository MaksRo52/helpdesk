import json
import secrets

from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (LoginView, PasswordChangeView,
                                       PasswordResetView)
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from config.settings import DOMAIN_MAIL, EMAIL_HOST_USER
from users.forms import (CustomPasswordChangeForm, UserRegisterForm,
                         UserUpdateForm)
from users.models import User
from users.services import ask_gemini, send_telegram_message
from users.tasks import authentication


class UserCreateView(generic.CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        user.is_active = True
        token = secrets.token_hex(16)
        user.token = token
        # П.1 Если требуется активация через почту домена.
        # user.email = f"{user.username}@{DOMAIN_MAIL}"
        user.save()
        # П.1 Если требуется активация через почту домена.
        # host = self.request.get_host()
        # url = f"https://{host}/users/activate/{token}/"
        # authentication.delay(url, user.email)
        return super().form_valid(form)

#П.1 Если требуется активация через почту домена.
# def email_verification(request, token):
#     user = get_object_or_404(User, token=token)
#     user.is_active = True
#     user.save()
#     return redirect(reverse("users:activate_account"))


class RecoveryPasswordView(PasswordResetView):
    template_name = "users/recovery_password.html"
    form_class = PasswordResetForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        try:
            user = User.objects.get(email=email)
            password = get_random_string(
                length=10,
                allowed_chars="abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789",
            )
            user.set_password(password)
            user.save(update_fields=["password"])
            send_mail(
                subject="Сброс пароля",
                message=f" Ваш новый пароль {password}",
                from_email=EMAIL_HOST_USER,
                recipient_list=[user.email],
            )
            return redirect(reverse("users:login"))
        except User.DoesNotExist:
            messages.error(self.request, "Пользователь с такой почтой не найден")
            return super().form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"Произошла ошибка: {str(e)}")
            return super().form_invalid(form)


class UserProfileView(generic.DetailView, LoginRequiredMixin):
    model = User
    template_name = "users/profile.html"


class CustomLoginView(LoginView):
    template_name = "users/login.html"

    def form_valid(self, form):
        if not form.user_cache.is_active:
            messages.error(self.request, "Аккаунт не активирован, проверьте почту")
            return self.form_invalid(form)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Неправильный логин или пароль")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse("main:index")


class UserUpdateView(generic.UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "users/update_profile.html"

    def get_success_url(self):
        return reverse_lazy("users:profile", kwargs={"pk": self.object.pk})

    def get_form_class(self):
        user = self.request.user
        if user == self.object:
            return UserUpdateForm
        raise PermissionDenied


class CustomPasswordChangeView(PasswordChangeView):
    model = User
    success_url = reverse_lazy("users:profile")
    form_class = CustomPasswordChangeForm
    template_name = "users/password_change.html"


# Настройка Telegram
waiting_for_login = {}


@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        data = json.loads(request.body)

        if "message" in data:
            chat_id = str(data["message"]["chat"]["id"])
            text = data["message"]["text"]

            if chat_id in waiting_for_login:
                del waiting_for_login[chat_id]  # Убираем из списка ожидания
                process_login(chat_id, text)
            else:
                if not is_chat_id_linked(
                    chat_id
                ):  # Проверяем, уже ли привязан этот chat_id
                    send_telegram_message.delay(
                        "Введите ваш логин (например, i.ivanov):", chat_id
                    )
                    waiting_for_login[chat_id] = True
                else:
                    ask_gemini.delay(text, chat_id)
                    send_telegram_message.delay("Ваш вопрос обрабатывается 🧠", chat_id)

        return JsonResponse({"status": "ok"}, status=200)

    return JsonResponse({"error": "Invalid request"}, status=400)


def is_chat_id_linked(chat_id):
    """Проверяет, привязан ли уже chat_id к пользователю"""
    return User.objects.filter(chat_id=chat_id).exists()


def process_login(chat_id, login):
    """Проверяет логин в базе и привязывает chat_id"""
    try:
        user = User.objects.get(username=login)

        if user.telegram_enabled:
            user.chat_id = chat_id
            user.save()
            send_telegram_message.delay(
                f"✅ Ваш chat_id успешно привязан к {login}!", chat_id
            )
            notify_admins(user)
        else:
            send_telegram_message.delay(
                "⚠ У вас не включена интеграция с Telegram.", chat_id
            )
    except User.DoesNotExist:
        send_telegram_message.delay(
            "❌ Пользователь с таким логином не найден.", chat_id
        )


def notify_admins(user):
    """Уведомляет админов о новом привязанном аккаунте"""
    admins = User.objects.filter(is_staff=True, telegram_enabled=True).exclude(
        chat_id=None
    )
    for admin in admins:
        send_telegram_message.delay(
            f"🔔 Пользователь {user.username} привязал Telegram!", admin.chat_id
        )


def developer(request):
    return render(request, "users/developer.html")
