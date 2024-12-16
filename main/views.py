from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, \
    View
from django.views.generic.detail import SingleObjectMixin
from main.forms import TaskForm, ModeratorTaskForm
from main.models import Task
from users.tasks import close_task, new_task, work_task
from django.core.exceptions import PermissionDenied

class TaskListView(LoginRequiredMixin, ListView):
    login_url = "users:login"
    model = Task


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    fields = "__all__"


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
        new_task.delay(task.title, task.pk, task.description, task.author.email)
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("main:index")


    def form_valid(self, form):
        task = form.save()
        user = self.request.user
        if task.status == "complete":
            close_task(task.title, task.commentary, task.author.email)
        return super().form_valid(form)

    def get_form_class(self):
        user = self.request.user
        if user == self.object.author:
            return TaskForm
        elif user.has_perm("main.can_edit_status_task"):
            return ModeratorTaskForm
        raise PermissionDenied

class TaskAtWork(SingleObjectMixin, View):
    model = Task

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        user = self.request.user
        if obj.status == "new":
            obj.status = "work"
            obj.save()
            work_task.delay(obj.title, obj.pk, user.email, obj.author.email)
        return HttpResponseRedirect(reverse_lazy('main:index'))


class TaskClose(SingleObjectMixin, View):
    model = Task

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.status == "new" or obj.status == "work":
            obj.status = "complete"
            obj.save()
            close_task(obj.title, obj.commentary, obj.author.email)
        return HttpResponseRedirect(reverse_lazy('main:index'))