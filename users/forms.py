from django import forms
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.forms import BooleanField, ModelForm

from users.models import User
from users.validations import validate_no_email


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    username = forms.CharField(
        label="Логин",
        max_length=250,
        required=True,
        validators=[validate_no_email],
        help_text="Введите ваш логин, например i.ivanov",
    )

    class Meta:
        model = User
        fields = (
            "username",
            "city",
            "password1",
            "password2",
        )

    def clean_username(self):
        username = self.cleaned_data["username"].lower()
        return username


class UserUpdateForm(StyleFormMixin, ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "city",
            "phone_number",
            "avatar",
            "telegram_enabled",
        )


class CustomPasswordChangeForm(StyleFormMixin, PasswordChangeForm):
    pass
