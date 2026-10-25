import os

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = os.environ.get("DEBUG") == "1"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "apps.core",
    "apps.accounts",
    "apps.billing",
]
TIME_ZONE = "UTC"
USE_TZ = True
CELERY_TASK_ALWAYS_EAGER = os.environ.get("CELERY_EAGER") == "1"
