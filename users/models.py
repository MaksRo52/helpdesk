from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

NULLABLE = {"null": True, "blank": True}


class User(AbstractUser):
    username = models.CharField(
        max_length=250,
        verbose_name="Логин",
        help_text="Введите ваш логин\nНапример i.ivanov",unique=True
    )
    email = models.EmailField(verbose_name="Email", **NULLABLE)
    token = models.CharField(
        max_length=100, verbose_name="Токен", null=True, blank=True
    )
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username