from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from main.models import Task, TaskComment

User = get_user_model()


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "author", "executor", "status")
    list_filter = ("author", "executor", "status")


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ("task", "author", "created_at", "content")
    list_filter = ("task", "author", "created_at")


class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User

    list_display = (
        "username",
        "email",
        "city",
        "is_active",
        "is_admin",
        "telegram_enabled",
    )
    list_filter = ("is_active", "is_admin", "last_login")

    def get_fieldsets(self, request, obj=None):
        if (
            obj is None
        ):  # Если объект не передан, значит, мы создаем нового пользователя
            fieldsets = (
                (
                    None,
                    {
                        "classes": ("wide",),
                        "fields": (
                            "username",
                            "email",
                            "city",
                            "password1",
                            "password2",
                            "is_active",
                            "is_admin",
                            "is_leader",
                        ),
                    },
                ),
            )
            if request.user.is_superuser:
                fieldsets += (
                    ("Superuser Permissions", {"fields": ("is_staff", "is_superuser")}),
                )
            return fieldsets

        fieldsets = (
            (None, {"fields": ("username", "email")}),
            (
                "Персональные данные",
                {
                    "fields": (
                        "first_name",
                        "last_name",
                        "city",
                        "phone_number",
                        "avatar",
                        "telegram_enabled",
                        "chat_id",
                    )
                },
            ),
            ("Права", {"fields": ("is_active", "is_admin", "is_leader", "groups")}),
            ("Даты", {"fields": ("last_login", "date_joined")}),
        )
        if request.user.is_superuser:
            fieldsets += (
                (
                    "Superuser Permissions",
                    {"fields": ("is_staff", "is_superuser", "user_permissions")},
                ),
            )

        return fieldsets


admin.site.register(User, CustomUserAdmin)
