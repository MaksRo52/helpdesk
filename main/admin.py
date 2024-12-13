from django.contrib import admin
from main.models import Task

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "token")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title",)
