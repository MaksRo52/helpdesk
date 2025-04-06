from django.contrib.auth.models import Group
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field

from users.models import User

NULLABLE = {"null": True, "blank": True}

STATUS_CHOICES = [
    ("new", "Создана"),
    ("work", "В работе"),
    ("complete", "Выполнена"),
    ("close", "Закрыта"),
]
CATEGORY_CHOICES = [
    ("access", "Предоставить/отключить доступ"),
    ("1c", "1С"),
    ("network", "Сеть и доступность"),
    ("directum", "Directum"),
    ("mail", "Вопросы по почте"),
    ("equipment", "Оборудование"),
    ("software", "Установка ПО"),
    ("other", "Другое"),
    ("auto_mods", "Автоматизация и доработки"),
]


class Task(models.Model):
    title = models.CharField(max_length=100, verbose_name="Тема")
    description = CKEditor5Field(
        verbose_name=_("Описание"),
        help_text=_("Введите описание"),
        config_name="extends",
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        verbose_name=_("Статус заявки"),
        choices=STATUS_CHOICES,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    start_date = models.DateTimeField(verbose_name="Дата начала выполнения", **NULLABLE)
    end_date = models.DateTimeField(
        verbose_name=_("Дата завершения выполнения"), **NULLABLE
    )
    priority = models.CharField(
        max_length=8,
        verbose_name="Приоритет",
        choices={"low": "Низкий", "medium": "Средний", "high": "Высокий"},
        **NULLABLE,
    )
    author = models.ForeignKey(
        User, verbose_name=_("автор"), on_delete=models.SET_NULL, **NULLABLE
    )
    img = models.ImageField(
        upload_to="task", **NULLABLE, verbose_name="Скриншот/фото проблемы"
    )
    file = models.FileField(upload_to="task", **NULLABLE, verbose_name=_("Файлы"))
    commentary = CKEditor5Field(verbose_name=_("Комментарий"), **NULLABLE)
    executor = models.ForeignKey(
        User,
        verbose_name=_("Исполнитель"),
        on_delete=models.SET_NULL,
        related_name="task_executor",
        **NULLABLE,
    )
    wishes = models.BooleanField(
        default=False, verbose_name=_("Утверждено"), help_text=_("Утвердить обращение")
    )
    anydesk = models.IntegerField(
        verbose_name="AnyDesk",
        help_text=_(
            "Введите номер AnyDesk для подключения. Загрузить AnyDesk можно внизу страницы."
        ),
        **NULLABLE,
    )
    coordinator = models.ForeignKey(
        User,
        verbose_name=_("Согласующий"),
        help_text=_("Укажите согласующего для утверждения заявки (При необходимости)"),
        on_delete=models.SET_NULL,
        related_name="coordinator",
        **NULLABLE,
    )
    category = models.CharField(
        max_length=50,
        verbose_name=_("Категория заявки"),
        choices=CATEGORY_CHOICES,
    )
    watcher = models.ManyToManyField(
        User,
        related_name="watcher",
        verbose_name=_("Наблюдатели"),
        help_text=_(
            "Укажите наблюдателей для заявки (При необходимости) Удерживайте “Control“)"
        ),
        blank=True,
    )

    def save(self, *args, **kwargs):
        if self.status == "work" and not self.start_date:
            self.start_date = now()
        elif self.status == "complete" and not self.end_date:
            self.end_date = now()
        if not self.executor:  # Если не указан исполнитель
            if self.category == "directum":
                try:
                    group = Group.objects.get(name="admin_directum")  # Получаем группу
                    first_user = group.user_set.order_by(
                        "id"
                    ).first()  # Берём первого пользователя
                    if first_user:
                        self.executor = first_user
                except Group.DoesNotExist:
                    pass  # Если группы нет, ничего не делаем

            elif self.category == "mail":
                try:
                    group = Group.objects.get(name="admin_mail")  # Получаем группу
                    first_user = group.user_set.order_by(
                        "id"
                    ).first()  # Берём первого пользователя
                    if first_user:
                        self.executor = first_user
                except Group.DoesNotExist:
                    pass  # Если группы нет, ничего не делаем
            elif self.category == "1c":
                try:
                    group = Group.objects.get(name="admin_1c")  # Получаем группу
                    first_user = group.user_set.order_by(
                        "id"
                    ).first()  # Берём первого пользователя
                    if first_user:
                        self.executor = first_user
                except Group.DoesNotExist:
                    pass  # Если группы нет, ничего не делаем
        super().save(*args, **kwargs)

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
    task = models.ForeignKey(
        Task, verbose_name="Задача", on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        User, verbose_name="Автор", on_delete=models.SET_NULL, **NULLABLE
    )
    content = CKEditor5Field(verbose_name="", config_name="extends", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Комментарий к задаче"
        verbose_name_plural = "Комментарии к задачам"
        ordering = ("created_at",)

        def __str__(self):
            return f"{self.author} - {self.task.title}"
