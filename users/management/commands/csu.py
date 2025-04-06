from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.create(username="administrator")
        user.set_password("admin")
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
