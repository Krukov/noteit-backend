# Parse database configuration from $DATABASE_URL
from .settings import *
import dj_database_url


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

) + INSTALLED_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
) + MIDDLEWARE_CLASSES


STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'
MEDIA_ROOT = 'media'
MEDIA_URL = '/media/'
ROOT_URLCONF = 'backend.urls_local'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# Enable Persistent Connections
import os

DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', None)
WSGI_APPLICATION = 'backend.wsgi.application'

DATABASES = {}
DATABASES['default'] = dj_database_url.config()
DATABASES['default']['CONN_MAX_AGE'] = 500

SSL = SECURE_SSL_REDIRECT = False
SECURE_FRAME_DENY = False

QUESTION_LIFE_TIME = {'seconds': 20}
MAX_NOTES = os.environ.get('NOTES_LIMIT', 10)