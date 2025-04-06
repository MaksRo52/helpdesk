from django.core.exceptions import ValidationError


def validate_no_email(value):
    if "@" in value:
        raise ValidationError(
            "Укажите только логин. Логин не является почтовым адресом"
        )
    elif "/" in value:
        raise ValidationError("Логин не может начинаться с 'corp/'")
    elif "\\" in value:
        raise ValidationError("Логин не может начинаться с 'corp\\'")
    elif "." not in value:
        raise ValidationError("Логин должен быть формата i.ivanov")
