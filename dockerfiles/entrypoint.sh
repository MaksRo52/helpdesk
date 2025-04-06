#!/bin/sh

set -e

echo "👉 Собираем статику..."
poetry run python manage.py collectstatic --noinput

echo "📦 Применяем миграции..."
poetry run python manage.py makemigrations
poetry run python manage.py migrate

echo "🌍 Компилируем переводы..."
poetry run python manage.py compilemessages -l en -l tr

echo "🚀 Запускаем Gunicorn..."
poetry run gunicorn config.wsgi:application --bind 0.0.0.0:8000