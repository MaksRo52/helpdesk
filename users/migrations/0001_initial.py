# Generated by Django 5.1.7 on 2025-03-21 12:50

import django.contrib.auth.models
import django.utils.timezone
import phonenumber_field.modelfields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        help_text="Введите ваш логин, например i.ivanov",
                        max_length=250,
                        unique=True,
                        verbose_name="Логин",
                    ),
                ),
                (
                    "city",
                    models.CharField(
                        choices=[
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
                        ],
                        help_text="Выберите город",
                        max_length=20,
                        verbose_name="Город",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, null=True, verbose_name="Email"
                    ),
                ),
                (
                    "is_admin",
                    models.BooleanField(
                        default=False, verbose_name="Системный администратор"
                    ),
                ),
                (
                    "is_leader",
                    models.BooleanField(default=False, verbose_name="Руководитель"),
                ),
                (
                    "token",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="Токен"
                    ),
                ),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True,
                        help_text="Введите номер мобильного телефона",
                        max_length=128,
                        region=None,
                        verbose_name="Номер телефона",
                    ),
                ),
                (
                    "chat_id",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        unique=True,
                        verbose_name="id чата телеграм",
                    ),
                ),
                (
                    "avatar",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="users",
                        verbose_name="Фото профиля",
                    ),
                ),
                (
                    "telegram_enabled",
                    models.BooleanField(
                        default=False, verbose_name="Телеграм оповещения"
                    ),
                ),
                (
                    "wa_id",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        unique=True,
                        verbose_name="id чата телеграм",
                    ),
                ),
                (
                    "whatsapp_enabled",
                    models.BooleanField(
                        default=False, verbose_name="WhatsApp оповещения"
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "Пользователь",
                "verbose_name_plural": "Пользователи",
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
