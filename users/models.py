from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

CITY_CHOICES = [
    ("nn", "Нижний Новгород"),
    ("msk", "Москва"),
    ("dnstr", "Донстрой"),
    ("kln", "Калининград"),
    ("kuz", "Кузьминки"),
    ("mg", "Магадан"),
    ("mrv", "Минеральные Воды"),
    ("nu", "Новый Уренгой"),
    ("omsk", "Омск"),
    ("ostr", "Остров 5"),
    ("vrn", "Воронеж"),
    ("pg", "Пермь Галерея"),
    ("tjm", "Тюмень"),
    ("yks", "Якутия"),
    ("other", "Другой"),
]

NULLABLE = {"null": True, "blank": True}


class User(AbstractUser):

    username = models.CharField(
        max_length=250,
        verbose_name=_("Логин"),
        help_text="Введите ваш логин, например i.ivanov",
        unique=True,
    )
    city = models.CharField(
        max_length=20,
        verbose_name=_("Город"),
        help_text=_("Выберите город"),
        choices=CITY_CHOICES,
    )
    email = models.EmailField(verbose_name="Email", **NULLABLE)
    is_admin = models.BooleanField(
        verbose_name="Системный администратор", default=False
    )
    is_leader = models.BooleanField(verbose_name="Руководитель", default=False)
    token = models.CharField(
        max_length=100, verbose_name="Токен", null=True, blank=True
    )
    phone_number = PhoneNumberField(
        verbose_name=_("Номер телефона"),
        help_text=_("Введите номер мобильного телефона"),
        blank=True,
    )
    chat_id = models.CharField(
        max_length=50, unique=True, verbose_name="id чата телеграм", **NULLABLE
    )
    avatar = models.ImageField(
        upload_to="users", **NULLABLE, verbose_name=_("Фото профиля")
    )
    telegram_enabled = models.BooleanField(
        verbose_name=_("Телеграм оповещения"), default=False
    )
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []
    wa_id = models.CharField(
        max_length=50, unique=True, verbose_name="id чата телеграм", **NULLABLE
    )
    whatsapp_enabled = models.BooleanField(
        verbose_name="WhatsApp оповещения", default=False
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
