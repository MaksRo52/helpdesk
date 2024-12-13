import secrets
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from django.views import generic
from config.settings import EMAIL_HOST_USER
from users.forms import UserRegisterForm
from users.models import User


class UserCreateView(generic.CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.email = f"{user.username}@limakmarash.com"
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/activate/{token}/"
        send_mail(
            subject="Активация аккаунта",
            message=f"Для активации вашего аккаунта перейдите по ссылке: {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse("users:login"))


class RecoveryPasswordView(PasswordResetView):
    template_name = "users/recovery_password.html"
    form_class = PasswordResetForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = User.objects.get(email=email)
        if user:
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


class UserProfileView(generic.DetailView):
    model = User
    template_name = "users/profile.html"
