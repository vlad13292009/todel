from .base import *
from decouple import config

SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-123')
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
