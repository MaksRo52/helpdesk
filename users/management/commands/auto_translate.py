import asyncio
import subprocess

import polib
from django.core.management.base import BaseCommand
from googletrans import Translator


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        subprocess.run(
            ["poetry", "run", "python", "manage.py", "makemessages", "-l", "tr"]
        )
        subprocess.run(
            ["poetry", "run", "python", "manage.py", "makemessages", "-l", "en"]
        )
        asyncio.run(self.main())
        subprocess.run(["poetry", "run", "python", "manage.py", "compilemessages"])

    async def translate_and_save(self, po_file, lang_code):
        translator = Translator()
        for entry in po_file.untranslated_entries():
            translated = await translator.translate(entry.msgid, dest=lang_code)
            entry.msgstr = translated.text

        po_file.save()
        self.stdout.write(
            self.style.SUCCESS(f"Файл переведён и сохранён для языка {lang_code}.")
        )

    async def main(self):
        po_tr = polib.pofile("locale/tr/LC_MESSAGES/django.po")
        po_en = polib.pofile("locale/en/LC_MESSAGES/django.po")

        await self.translate_and_save(po_tr, "tr")
        await self.translate_and_save(po_en, "en")
