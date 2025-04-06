import os
from pathlib import Path

from celery.schedules import crontab
from dotenv import load_dotenv

from config.ckeditor_config import *

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", False) == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "users",
    "main",
    "rest_framework",
    "django_ckeditor_5",
    "drf_yasg",
    "phonenumber_field",
    "django_select2",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


LANGUAGE_CODE = "ru"

LANGUAGES = [
    ("en", "English"),
    ("tr", "Türkçe"),
    ("ru", "Русский"),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

MEDIA_URL = "media/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATIC_URL = "static/"

ENV_TYPE = os.getenv("ENV_TYPE")

if ENV_TYPE == "local":
    STATICFILES_DIRS = (BASE_DIR / "static",)
else:
    STATIC_ROOT = BASE_DIR / "static"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DOMAIN_MAIL = os.getenv("DOMAIN_MAIL")

LOGIN_REDIRECT_URL = "/"

AUTH_USER_MODEL = "users.User"
LOGOUT_REDIRECT_URL = "main:index"

# Настройки почты
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", False) == "True"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", False) == "True"

# Логирование ошибок
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"}
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "default"}},
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {"django": {"handlers": ["console"], "propagate": False}},
}

# Настройки для Celery

CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL"
)  # Например, Redis, который по умолчанию работает на порту 6379
# URL-адрес брокера результатов, также Redis
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
# Часовой пояс для работы Celery
CELERY_TIMEZONE = TIME_ZONE
# Флаг отслеживания выполнения задач
CELERY_TASK_TRACK_STARTED = True
# Максимальное время на выполнение задачи
CELERY_TASK_TIME_LIMIT = 30 * 60

CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

LOGIN_URL = "users:login"

TELEGRAM_URL = "https://api.telegram.org/bot"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")

# CACHES

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("LOCATION_CACHE"),
    },
    "select2": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("LOCATION_REDIS"),
    },
}

# Tell select2 which cache configuration to use:
SELECT2_CACHE_BACKEND = "select2"

# Celery Beat Scheduler
CELERY_BEAT_SCHEDULE = {
    "auto-close-tasks-everyday": {
        "task": "users.tasks.auto_close_task",
        "schedule": crontab(hour="*/1"),
    },
}

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SESSION_SAVE_EVERY_REQUEST = True  # опционально, чтобы всегда сохранялась сессия
SESSION_ENGINE = "django.contrib.sessions.backends.db"
