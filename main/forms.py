import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BooleanField, ModelForm
from django_ckeditor_5.widgets import CKEditor5Widget
from django_select2.forms import Select2MultipleWidget, Select2Widget

from main.models import Task, TaskComment
from users.models import User


class StyleFormMixin(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == "description" or field_name == "content":
                continue
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class TaskForm(StyleFormMixin, ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False

        if self.user and self.user.is_leader:
            # Ограничиваем список executor только пользователями с is_admin=True
            self.fields["executor"].queryset = User.objects.filter(is_admin=True)
        else:
            # Удаляем поле executor, если пользователь не руководитель
            self.fields.pop("executor")

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        watchers = cleaned_data.get("watcher")
        coordinator = cleaned_data.get("coordinator")
        executor = cleaned_data.get("executor")
        author = self.user

        # Проверка, что автор не является координатором или наблюдателем
        if author:
            if coordinator == author:
                raise ValidationError("Автор не может быть согласующим.")
            if watchers and author in watchers:
                raise ValidationError("Автор не может быть наблюдателем.")

        # Проверка на дублирование координатора и наблюдателей
        if coordinator and watchers and coordinator in watchers:
            raise ValidationError(
                "Пользователь не может быть одновременно наблюдателем и согласующим."
            )

        # Проверка на дублирование исполнителя в наблюдателях и координаторе
        if executor:
            if watchers and executor in watchers:
                raise ValidationError("Исполнитель не может быть наблюдателем.")
            if coordinator and executor == coordinator:
                raise ValidationError("Исполнитель не может быть согласующим.")

        if not executor:
            if category == "directum":
                if watchers:
                    for user in watchers:
                        if user.groups.filter(name="admin_directum").exists():
                            raise ValidationError(
                                f"Вы не можете добавлять наблюдателя {user} для категории 'Directum'."
                            )
                if (
                    coordinator
                    and coordinator.groups.filter(name="admin_directum").exists()
                ):
                    raise ValidationError(
                        f"Вы не можете добавлять согласующего {coordinator.username} для категории 'Directum'."
                    )

            if category == "mail":
                if watchers:
                    for user in watchers:
                        if user.groups.filter(name="admin_mail").exists():
                            raise ValidationError(
                                f"Вы не можете добавлять наблюдателя {user} для категории 'Вопросы по почте'."
                            )
                if (
                    coordinator
                    and coordinator.groups.filter(name="admin_mail").exists()
                ):
                    raise ValidationError(
                        f"Вы не можете добавлять согласующего {coordinator.username} для категории 'Вопросы по почте'."
                    )

            if category == "1c":
                if watchers:
                    for user in watchers:
                        if user.groups.filter(name="admin_1c").exists():
                            raise ValidationError(
                                f"Вы не можете добавлять наблюдателя {user} для категории '1С'."
                            )
                if coordinator and coordinator.groups.filter(name="admin_1c").exists():
                    raise ValidationError(
                        f"Вы не можете добавлять согласующего {coordinator.username} для категории '1С'."
                    )

        # if category not in ["access", "auto_mods"] and coordinator:
        #     raise ValidationError(
        #         "Согласующий не требуется для выбранной категории.")

        return cleaned_data

    class Meta:
        model = Task
        fields = (
            "category",
            "title",
            "anydesk",
            "description",
            "executor",
            "watcher",
            "coordinator",
        )
        widgets = {
            "watcher": Select2MultipleWidget(
                attrs={"data-placeholder": "Выберите наблюдателей"}
            ),
            "coordinator": Select2Widget(
                attrs={"data-placeholder": "Выберите согласующего"}
            ),
            "description": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            ),
        }


class ModeratorTaskForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Task
        fields = (
            "executor",
            "watcher",
            "coordinator",
        )
        widgets = {
            "watcher": Select2MultipleWidget(
                attrs={"data-placeholder": "Выберите наблюдателей"}
            ),
            "coordinator": Select2Widget(
                attrs={"data-placeholder": "Выберите согласующего"}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        # Получаем текущего пользователя
        super().__init__(*args, **kwargs)

        if user and user.is_leader:
            # Ограничиваем список executor только пользователями с is_admin=True
            self.fields["executor"].queryset = User.objects.filter(is_admin=True)
        else:
            # Удаляем поле executor, если пользователь не руководитель
            self.fields.pop("executor")


class CommentaryTaskForm(StyleFormMixin, ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].required = False

    class Meta:
        model = TaskComment
        fields = ("content",)
        widgets = {
            "id": "comment-content",
            "content": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            ),
        }

    def clean_content(self):
        content = self.cleaned_data.get("content", "").strip()
        text_only = re.sub(r"<[^>]+>", "", content).replace("&nbsp;", "").strip()
        if not text_only:
            raise forms.ValidationError("Комментарий не может быть пустым!")
        return content


class CoordinatorTaskForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Task
        fields = ("wishes", "status", "executor", "watcher")
        widgets = {
            "watcher": Select2MultipleWidget(
                attrs={"data-placeholder": "Выберите наблюдателей"}
            ),
        }
