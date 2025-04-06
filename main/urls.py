from django.urls import path

from main.apps import MainConfig
from main.views import (TaskAtWork, TaskClose, TaskCreateView, TaskDetailView,
                        TaskListView, TaskRefuse, TaskUpdateView, TaskWhishes,
                        ask_gemini_api, clear_context, stream_gemini)
from users.views import telegram_webhook

app_name = MainConfig.name


urlpatterns = [
    path("", TaskListView.as_view(), name="index"),
    path("create/", TaskCreateView.as_view(), name="task_create"),
    path("task/<int:pk>", TaskDetailView.as_view(), name="task_detail"),
    path("task_update/<int:pk>", TaskUpdateView.as_view(), name="task_update"),
    path("task/work/<int:pk>", TaskAtWork.as_view(), name="task_at_work"),
    path("task/close/<int:pk>", TaskClose.as_view(), name="task_close"),
    path("task/whishes/<int:pk>", TaskWhishes.as_view(), name="task_whishes"),
    path("task/refuse/<int:pk>", TaskRefuse.as_view(), name="task_refuse"),
    path("webhook/", telegram_webhook, name="webhook"),
    path("ask-gemini/", ask_gemini_api, name="ask_gemini_api"),
    path("stream-gemini/", stream_gemini, name="stream_gemini"),
    path("clear-context/", clear_context, name="clear_context"),
    # path("whatsapp_webhook/", whatsapp_webhook, name="whatsapp_webhook"),
]
