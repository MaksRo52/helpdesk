from celery import shared_task
from django.core.mail import send_mail
from config.settings import EMAIL_HOST_USER


@shared_task
def authentication(url,email):
    send_mail(
        subject="Активация аккаунта",
        message=f"Для активации вашего аккаунта перейдите по ссылке: {url}",
        from_email=EMAIL_HOST_USER,
        recipient_list=[email],
    )
