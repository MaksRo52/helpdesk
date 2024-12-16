from django.urls import path

from main.apps import MainConfig
from main.views import (TaskCreateView, TaskDetailView, TaskListView,
                        TaskUpdateView, TaskAtWork)

app_name = MainConfig.name


urlpatterns = [
    path("", TaskListView.as_view(), name="index"),
    path("create/", TaskCreateView.as_view(), name="task_create"),
    path("task/<int:pk>", TaskDetailView.as_view(), name="task_detail"),
    path("task_update/<int:pk>", TaskUpdateView.as_view(), name="task_update"),
    path("task/work/<int:pk>", TaskAtWork.as_view(), name="task_at_work"),
]
