from django.db import models

NULLABLE = {"null": True, "blank": True}
from users.models import User


class Task(models.Model):
    title = models.CharField(max_length=100, verbose_name="Тема")
    description = models.TextField(
        verbose_name="Описание", help_text="Введите описание"
    )
    status = models.CharField(
        max_length=8,
        verbose_name="Статус заявки",
        choices={"new": "Создана", "work": "В работе", "complete": "Выполнена"},
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    priority = models.CharField(
        max_length=8,
        verbose_name="Приоритет",
        choices={"low": "Низкий", "medium": "Средний", "high": "Высокий"},
    )
    author = models.ForeignKey(
        User, verbose_name="автор", on_delete=models.SET_NULL, **NULLABLE
    )
    img = models.ImageField(**NULLABLE, verbose_name="Скриншот/фото проблемы")
    commentary = models.CharField(
        max_length=500, verbose_name="Комментарий", **NULLABLE
    )


    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        permissions = [
            ("can_edit_status_task", "Can edit status task"),
        ]

        def __str__(self):
            return self.title



class TaskComment(models.Model):
    task = models.ForeignKey(Task, verbose_name="Задача", on_delete=models.CASCADE)
    author = models.ForeignKey(
        User, verbose_name="Автор", on_delete=models.SET_NULL, **NULLABLE
    )
    content = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Комментарий к задаче"
        verbose_name_plural = "Комментарии к задачам"
        ordering = ("-created_at",)

        def __str__(self):
            return f"{self.author} - {self.task.title}"
