from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

NULLABLE = {"null": True, "blank": True}


class User(AbstractUser):
    username = models.CharField(
        max_length=250,
        verbose_name="Логин",
        help_text="Введите ваш логин\nНапример i.ivanov", unique=True
    )
    city = models.CharField(max_length=20,
                            verbose_name="Город", help_text="Выберите город",
                            choices={"nn": "Нижний Новгород", "msk": "Москва",
                                     "dnstr": "Донстрой", "kln": "Калининград",
                                     "kuz": "Кузьминки",
                                     "mg": "Магадан",
                                     "mrv": "Минеральные Воды",
                                     "nu": "Новый Уренгой",
                                     "omsk": "Омск",
                                     "ostr": "Остров 5",
                                     "vrn": "Воронеж",
                                     "pg": "Пермь Галерея",
                                     "tjm": "Тюмень",
                                     "yks": "Якутия",
                                     "Other": "Другой"
                                     }, **NULLABLE)
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
