import os

BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

DEBUG = False

INSTALLED_APPS = (
    'noteit',	
)


MIDDLEWARE_CLASSES = (
    'noteit.middlewares.TokenAuthentication',
    'noteit.middlewares.BasicAuthMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'noteit.urls'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
