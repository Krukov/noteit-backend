import os

BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

DEBUG = False

INSTALLED_APPS = (
    'send',
    'send.users',
)

APP_USER_MODEL = 'users.User'

MIDDLEWARE_CLASSES = (
    'send.users.middlewares.TokenAuthentication',
    'send.users.middlewares.BasicAuthMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'send.urls'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
