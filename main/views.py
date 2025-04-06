import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import (Http404, HttpResponseRedirect, JsonResponse,
                         StreamingHttpResponse)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (CreateView, DetailView, ListView, UpdateView,
                                  View)
from django.views.generic.detail import SingleObjectMixin

from main.forms import CommentaryTaskForm, ModeratorTaskForm, TaskForm
from main.models import CATEGORY_CHOICES, STATUS_CHOICES, Task
from users.models import CITY_CHOICES
from users.services import process_gemini_for_web, stream_gemini_response
from users.tasks import (close_task, coordinator_task, new_comment_task,
                         new_executor, new_task, new_task_admin, new_watcher,
                         work_task)

from .models import User


class TaskListView(LoginRequiredMixin, ListView):
    paginate_by = 20
    login_url = "users:login"
    model = Task

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.all()

        # Фильтрация по статусу
        status_filter = self.request.GET.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Фильтрация по городу
        city_filter = self.request.GET.get("city")
        if city_filter:
            queryset = queryset.filter(author__city=city_filter)

        my_task_filter = self.request.GET.get("my_tasks")
        if my_task_filter:
            queryset = queryset.filter(executor=user)

        category_filter = self.request.GET.get("category")
        if category_filter:
            queryset = queryset.filter(category=category_filter)

        show_all_filter = self.request.GET.get("show_all")
        if status_filter != "close":
            if not show_all_filter:
                queryset = queryset.filter().exclude(status="close")

        # Логика фильтрации для разных типов пользователей
        if user.is_superuser or user.is_staff:
            return queryset
        elif user.is_admin:
            return (
                queryset.filter(author__city=user.city, executor__isnull=True)
                | queryset.filter(executor=user)
                | queryset.filter(coordinator=user)
                | queryset.filter(watcher=user)
            )
        else:
            return (
                queryset.filter(author=user)
                | queryset.filter(coordinator=user)
                | queryset.filter(watcher=user)
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context["tasks"] = queryset
        context["statuses"] = STATUS_CHOICES
        context["categories"] = CATEGORY_CHOICES
        context["cities"] = CITY_CHOICES
        context["total_task_count"] = queryset.count()
        return context

    def render_to_response(self, context, **response_kwargs):
        # Если запрос AJAX, вернуть только частичный шаблон
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return render(self.request, "main/partials/task_list_dynamic.html", context)
        # Иначе вернуть полный шаблон
        return super().render_to_response(context, **response_kwargs)


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = "task"

    def dispatch(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=self.kwargs["pk"])
        user = request.user

        # Проверка суперпользователя и персонала
        if user.is_superuser or user.is_staff:
            return super().dispatch(request, *args, **kwargs)

        # Проверка для админа
        if getattr(user, "is_admin", False):  # безопасный доступ к атрибуту
            if (
                task.author and task.author.city == user.city and task.executor is None
            ) or task.executor == user:
                return super().dispatch(request, *args, **kwargs)

        # Проверка для обычных пользователей
        if (
            user in {task.author, task.coordinator, task.executor}
            or user in task.watcher.all()
        ):
            return super().dispatch(request, *args, **kwargs)

        raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        context["comments"] = task.comments.all()  # Получение комментариев
        context["form"] = CommentaryTaskForm()  # Форма для нового комментария
        return context

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        form = CommentaryTaskForm(request.POST)
        host = self.request.get_host()
        url = f"https://{host}/task/{task.pk}"
        if task.status != "close":
            if form.is_valid():
                comment = form.save(commit=False)
                comment.task = task
                comment.author = request.user
                comment.save()

                # Определяем получателей
                recipients = []
                if task.executor and task.executor != request.user:
                    recipients.append(task.executor.email)
                if task.coordinator and task.coordinator != request.user:
                    recipients.append(task.coordinator.email)
                if task.author and task.author != request.user:
                    recipients.append(task.author.email)
                if task.watcher:
                    recipients.extend(
                        task.watcher.exclude(id=request.user.id).values_list(
                            "email", flat=True
                        )
                    )

                # Убираем дублирующиеся email-адреса
                recipients = list(set(recipients))
                print(recipients)

                # Отправляем задачу
                new_comment_task.delay(task.title, url, recipients)

                return HttpResponseRedirect(reverse("main:task_detail", args=[task.pk]))
            else:
                return self.get(request, *args, **kwargs)


class TaskCreateView(LoginRequiredMixin, CreateView):
    login_url = "users:login"
    redirect_field_name = "redirect_to"
    model = Task
    form_class = TaskForm

    def get_success_url(self):
        return reverse_lazy("main:task_detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        task = form.save(commit=False)
        user = self.request.user
        task.author = user
        task.status = "new"
        task.save()

        # Рассылка уведомлений
        host = self.request.get_host()
        url = f"https://{host}/task/{task.pk}"
        admin_emails = []
        watcher_emails = []
        new_task.delay(task.title, task.pk, url, task.author.email)
        # Заполняем список наблюдателей
        if task.watcher:
            watcher_emails.extend(
                task.watcher.exclude(id=user.id).values_list("email", flat=True)
            )
        # Заполняем список админов по городу
        for admin in User.objects.filter(is_admin=True, city=task.author.city):
            if admin.email:
                admin_emails.append(admin.email)

        if task.executor:
            new_executor.delay(
                task.title,
                task.pk,
                url,
                task.executor.email,
            )
        else:
            new_task_admin.delay(task.title, task.pk, url, admin_emails)
        if task.watcher:
            new_watcher.delay(
                task.title,
                task.pk,
                url,
                watcher_emails,
            )
        if task.coordinator:
            coordinator_task.delay(task.title, task.pk, url, [task.coordinator.email])
        return super().form_valid(form)

    def form_invalid(self, form):
        """Показать ошибки для каждого поля и общие ошибки"""
        for field, errors in form.errors.items():
            if field in form.fields:
                for error in errors:
                    messages.error(self.request, f"{form.fields[field].label}: {error}")
            else:
                # Для общих ошибок (из clean)
                for error in errors:
                    messages.error(self.request, error)

        return super().form_invalid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    login_url = "users:login"
    model = Task
    form_class = TaskForm

    def get_success_url(self):
        return reverse_lazy("main:task_detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        form_class = self.get_form_class()
        if form_class in [TaskForm, ModeratorTaskForm]:
            kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        task = form.save(commit=False)  # Сохраняем форму, но не коммитим в БД
        old_task = Task.objects.get(pk=task.pk)  # Получаем старую версию объекта из БД

        host = self.request.get_host()
        url = f"https://{host}/task/{task.pk}"

        # Проверяем изменение координатора
        if (
            old_task.coordinator != task.coordinator
            and task.coordinator
            and not task.wishes
        ):
            coordinator_task.delay(task.title, task.pk, url, [task.coordinator.email])

        # Проверяем изменение статуса на "complete"
        if old_task.status != "complete" and task.status == "complete":
            close_task(task.title, task.commentary, task.author.email)

        # Проверяем изменение исполнителя
        if old_task.executor != task.executor and task.executor:
            new_executor.delay(task.title, task.pk, url, task.executor.email)

        task.save()  # Теперь сохраняем изменения в БД

        return super().form_valid(form)

    def get_form_class(self):
        user = self.request.user
        if self.object.status != "complete":
            if user == self.object.author:
                return TaskForm
            # elif user == self.object.coordinator:
            #     return CoordinatorTaskForm
            elif user.is_admin and user != self.object.author:
                return ModeratorTaskForm
        raise PermissionDenied


class TaskAtWork(SingleObjectMixin, View):
    model = Task

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        user = self.request.user
        if obj.status == "new" or obj.status == "complete":
            obj.status = "work"
            obj.executor = user
            obj.save()
            work_task.delay(obj.title, obj.pk, user.email, obj.author.email)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


class TaskClose(SingleObjectMixin, View):
    model = Task

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        user = self.request.user
        if obj.status == "new" or obj.status == "work":
            obj.status = "complete"
            obj.executor = user
            obj.save()
            if obj.author != obj.executor:
                close_task.delay(obj.title, obj.author.email)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


class TaskWhishes(SingleObjectMixin, View):
    model = Task

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        commentary = request.POST.get("commentary")
        if obj.status == "new" or obj.status == "work":
            obj.wishes = True
            obj.commentary = commentary
            obj.save()

        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


class TaskRefuse(SingleObjectMixin, View):
    model = Task

    def post(self, request, *args, **kwargs):
        user = self.request.user
        obj = self.get_object()
        commentary = request.POST.get("commentary")

        # Сохраняем комментарий и меняем статус задачи
        obj.executor = user
        obj.commentary = commentary
        obj.status = "complete"
        obj.save()

        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


@csrf_exempt
def stream_gemini(request):
    prompt = request.GET.get("prompt", "").strip()
    if not prompt:
        return StreamingHttpResponse(
            ("data: ❌ Пустой запрос\n\n" for _ in range(1)),
            content_type="text/event-stream",
        )

    context = request.session.get("gemini_context", []).copy()
    context.append({"role": "user", "parts": [{"text": prompt}]})

    request.session["gemini_context"] = context
    request.session.modified = True

    def generate_stream():
        full_response_text = ""

        # Стриминг данных
        for chunk in stream_gemini_response(context):
            yield chunk
            text_chunk = chunk.replace("data: ", "").replace("<br>", "\n").strip()
            full_response_text += text_chunk

        # После завершения генерации добавляем ответ модели
        context.append({"role": "model", "parts": [{"text": full_response_text}]})

        # Очень важно: Сохраняем явно обратно в сессию именно тут
        request.session["gemini_context"] = context
        request.session.modified = True

        # Важный хак: дополнительный пустой yield, чтобы Django закрыл соединение
        yield "\n\n"

    response = StreamingHttpResponse(
        generate_stream(),
        content_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

    return response


def clear_context(request):
    request.session.pop("gemini_context", None)
    request.session.modified = True
    return JsonResponse({"status": "контекст очищен"})


@csrf_exempt
def ask_gemini_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        prompt = data.get("prompt", "")

        if not prompt:
            return JsonResponse({"answer": "❌ Пустой запрос"}, status=400)

        # Вызов нейросети
        answer = process_gemini_for_web(prompt)

        return JsonResponse({"answer": answer})

    return JsonResponse({"answer": "❌ Метод не поддерживается"}, status=405)
