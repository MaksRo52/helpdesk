from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from main.forms import ModeratorTaskForm, TaskForm
from main.models import Task

from config.settings import EMAIL_HOST_USER


class TaskListView(LoginRequiredMixin, ListView):
    login_url = "users:login"
    model = Task


class TaskDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Task
    fields = "__all__"
    permission_required = "view_detail_task"

    def has_permission(self):
        obj = self.get_object()
        user = self.request.user
        return obj.autor == user

    def get_name(request):
        if request.method == "POST":
            form = CommentaryTaskForm(request.POST)
            if form.is_valid():
                # Сохранение формы
                form.save()
                return HttpResponseRedirect(request.path_info)
        else:
            # метод GET

            form = CommentaryTaskForm()

            # Получение всех имен из БД.
            names = CommentaryTaskForm.objects.all()

            # И добавляем names в контекст, чтобы плучить к ним доступ в шаблоне
        return render(request, "name.html", {"form": form, "names": names})


class TaskCreateView(LoginRequiredMixin, CreateView):
    login_url = "users:login"
    redirect_field_name = "redirect_to"
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("main:index")

    def form_valid(self, form):
        task = form.save()
        user = self.request.user
        task.author = user
        task.status = "new"
        task.save()
        send_mail(
            subject=f"Создана задача {task.title}",
            message=f' Была создана задача "{task.title}" под номером {task.pk} :\n'
            f"{task.description}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[task.author.email],
        )
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("main:index")

    def get_form_class(self):
        user = self.request.user
        if user == self.object.author:
            return TaskForm
        elif user.has_perm("edit_task") or user.has_perm("delete_tasks"):
            return ModeratorTaskForm
        raise PermissionDenied

    def form_valid(self, form):
        task = form.save()
        user = self.request.user
        if task.status == "complete":
            send_mail(
                subject=f'Задача "{task.title}" завершена',
                message=f'Задача "{task.title}" завершена. \n Решение: \n'
                f"{task.commentary}",
                from_email=EMAIL_HOST_USER,
                recipient_list=[task.author.email],
            )
        elif task.status == "work":
            send_mail(
                subject=f'Задача "{task.title}" принята в работу',
                message=f'Задача "{task.title}" под номером {task.pk} Была принята в работу {user.email}',
                from_email=EMAIL_HOST_USER,
                recipient_list=[task.author.email],
            )

        return super().form_valid(form)
