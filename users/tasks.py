from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now

from config.settings import EMAIL_HOST_USER
from main.models import Task
from users.models import User
from users.services import send_telegram_message


@shared_task
def authentication(url, email):
    send_mail(
        subject="Активация аккаунта",
        message=f"Для активации вашего аккаунта перейдите по ссылке: {url}",
        from_email=EMAIL_HOST_USER,
        recipient_list=[email],
    )


@shared_task
def new_task(title, pk, url, email):
    send_mail(
        subject=f"(#HD-{pk}) {title}",
        message=f'Здравствуйте,\nЭто автоматический ответ.\n\n\nВаше обращение "{title}" зарегистрировано под номером #HD-{pk}.:\n'
        f"Ссылка на обращение {url}",
        from_email=EMAIL_HOST_USER,
        recipient_list=[email],
    )


@shared_task
def new_task_admin(title, pk, url, admin_emails):
    send_mail(
        subject=f'(#HD-{pk}) Создано обращение "{title}"',
        message=f'Здравствуйте,\nЭто автоматический ответ.\n\n\nСоздано обращение "{title}" .\nСсылка на заявку {url}',
        from_email=EMAIL_HOST_USER,
        recipient_list=admin_emails,
    )
    for user in User.objects.filter(email__in=admin_emails):
        if user.chat_id:
            send_telegram_message.delay(
                f'Создано обращение "{title}" .\nСсылка на заявку {url}', user.chat_id
            )


@shared_task
def work_task(title, pk, email, author_email):
    send_mail(
        subject=f'(#HD-{pk}) Обращение "{title}" принято в работу',
        message=f'Здравствуйте,\nЭто автоматический ответ.\n\n\nВаше обращение "{title}" было принято в работу.\nОтветственный по вашей заявке: {email}',
        from_email=EMAIL_HOST_USER,
        recipient_list=[author_email],
    )


@shared_task
def close_task(title, email):
    send_mail(
        subject=f'Обращение "{title}" закрыто',
        message=f'Здравствуйте,\nЭто автоматический ответ.\n\n\nВаше обращение "{title}" закрыто.\n',
        from_email=EMAIL_HOST_USER,
        recipient_list=[email],
    )


@shared_task
def coordinator_task(title, pk, url, email):
    send_mail(
        subject=f"Необходимо утвердить обращение '{pk}'",
        message=f'Здравствуйте,\nЭто автоматический ответ.\n\n\nБыло создано обращение "{title}" по адресу {url} \nНеобходимо ваше подтверждение.',
        from_email=EMAIL_HOST_USER,
        recipient_list=email,
    )
    for user in User.objects.filter(email=email):
        if user.chat_id:
            send_telegram_message.delay(
                f'Необходимо Ваше подтверждение по обращению "{title}". Адрес {url} \n',
                user.chat_id,
            )


@shared_task
def new_executor(title, pk, url, email):
    send_mail(
        subject=f"Назначен ответственным по обращению (#HD-{pk})",
        message=f'Здравствуйте,\nЭто автоматический ответ.\n\n\nВы были назначены ответственным по обращению "{title}" .\n'
        f"Ссылка на обращение {url}",
        from_email=EMAIL_HOST_USER,
        recipient_list=[email],
    )
    for user in User.objects.filter(email=email):
        if user.chat_id:
            send_telegram_message.delay(
                f'Вы были назначены ответственным по обращению "{title}".\nСсылка на обращение {url}',
                user.chat_id,
            )


@shared_task
def new_watcher(title, pk, url, email):
    send_mail(
        subject=f"Назначен наблюдателем по обращению (#HD-{pk})",
        message=f'Здравствуйте,\nЭто автоматический ответ.\n\n\nВы были назначены наблюдателем по обращению "{title}" .\n'
        f"Ссылка на обращение {url}",
        from_email=EMAIL_HOST_USER,
        recipient_list=email,
    )


@shared_task
def new_comment_task(title, url, email):
    send_mail(
        subject=f'Новый комментарий к обращению "{title}"',
        message=f'Здравствуйте,\nЭто автоматический ответ.\n\n\nВ обращении "{title}" был добавлен новый комментарий.\n'
        f"Ссылка на обращение {url}",
        from_email=EMAIL_HOST_USER,
        recipient_list=email,
    )
    for user in User.objects.filter(email__in=email):
        if user.chat_id:
            send_telegram_message.delay(
                f'Новый комментарий к обращению "{title}"\nСсылка на обращение {url}',
                user.chat_id,
            )


@shared_task
def auto_close_task():
    cutoff_time = now() - timedelta(days=1)
    tasks_to_close = Task.objects.filter(status="complete", end_date__lt=cutoff_time)

    for task in tasks_to_close:
        task.status = "close"
        task.save()

    # if tasks_to_close.count() != 0:
    #     admins = User.objects.filter(is_staff=True, telegram_enabled=True).exclude(
    #         chat_id=None
    #     )
    #     for admin in admins:
    #         send_telegram_message(
    #             f"Было закрыто {tasks_to_close.count()} обращений", admin.chat_id
    #         )
    #
    # return f"Всего {tasks_to_close.count()} обращений было закрыто."
