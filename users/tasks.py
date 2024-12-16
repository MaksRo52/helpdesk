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


@shared_task
def new_task(title, pk, description, email):
    send_mail(
        subject=f"Создана задача {title}",
        message=f' Была создана задача "{title}" под номером {pk} :\n'
                f"{description}",
        from_email=EMAIL_HOST_USER,
        recipient_list=[email],
    )

@shared_task
def work_task(title, pk, email, author_email):
    send_mail(
        subject=f'Задача "{title}" принята в работу',
        message=f'Задача "{title}" под номером {pk} Была принята в работу {email}',
        from_email=EMAIL_HOST_USER,
        recipient_list=[author_email],
    )

@shared_task
def close_task(title, commentary, email):
    send_mail(
        subject=f'Задача "{title}" завершена',
        message=f'Задача "{title}" завершена. \n Решение: \n'
                f"{commentary}",
        from_email=EMAIL_HOST_USER,
        recipient_list=[email],
    )