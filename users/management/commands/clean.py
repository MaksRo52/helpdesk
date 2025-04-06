import os
import re

from django.conf import settings
from django.core.management.base import BaseCommand

from main.models import Task


class Command(BaseCommand):
    help = "Удаляет файлы из папки media, которые не привязаны к объектам базы данных"

    def handle(self, *args, **kwargs):
        media_root = settings.MEDIA_ROOT  # Путь к папке media
        media_files = self.get_all_media_files(media_root)  # Все файлы в папке media
        used_files = self.get_used_files()  # Файлы, привязанные к моделям и полям

        # Приводим пути к единому виду
        media_files = {os.path.normpath(file) for file in media_files}
        used_files = {os.path.normpath(file) for file in used_files}

        self.stdout.write("Файлы в папке media:")
        for file in media_files:
            self.stdout.write(f" - {file}")

        self.stdout.write("\nФайлы, используемые в базе данных:")
        for file in used_files:
            self.stdout.write(f" - {file}")

        # Проверяем, какие файлы не используются
        unused_files = media_files - used_files

        self.stdout.write("\nФайлы, которые будут удалены:")
        for file in unused_files:
            self.stdout.write(f" - {file}")

        # Удаляем неиспользуемые файлы
        # for file_path in unused_files:
        #     os.remove(file_path)
        #     self.stdout.write(self.style.SUCCESS(f"Deleted: {file_path}"))
        #
        # self.stdout.write(self.style.SUCCESS("Unused files cleanup completed."))

    def get_all_media_files(self, media_root):
        """
        Возвращает множество всех файлов в папке media.
        """
        all_files = set()
        for root, dirs, files in os.walk(media_root):
            for file in files:
                all_files.add(os.path.join(root, file))
        return all_files

    def get_used_files(self):
        """
        Собирает файлы, которые используются в базе данных.
        """
        used_files = set()

        # 1. Поле image (ImageField)
        for task in Task.objects.all():
            if task.img:
                full_path = self.get_full_path(task.img.name)
                self.stdout.write(f"Добавлен файл из Task.img: {full_path}")
                used_files.add(full_path)

            # 2. Поле description (CKEditor)
            if task.description:
                description_files = self.extract_files_from_html(task.description)
                self.stdout.write(f"Файлы из Task.description: {description_files}")
                used_files.update(description_files)

        return used_files

    @staticmethod
    def extract_files_from_html(html_content):
        """
        Извлекает пути файлов из HTML-содержимого.
        """
        media_files = set()
        media_url = settings.MEDIA_URL.strip("/")  # Удаляем лишние слэши

        # Регулярное выражение для поиска ссылок на файлы в HTML
        file_pattern = re.compile(rf'{media_url}/([^"\'\s>]+)')

        # Ищем ссылки на файлы
        matches = file_pattern.findall(html_content)
        for match in matches:
            # Конструируем полный путь файла
            file_path = os.path.join(settings.MEDIA_ROOT, match)
            media_files.add(file_path)

        return media_files

    @staticmethod
    def get_full_path(relative_path):
        """
        Возвращает полный путь к файлу из относительного пути.
        """
        return os.path.normpath(os.path.join(settings.MEDIA_ROOT, relative_path))
