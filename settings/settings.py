import os

BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

DEBUG = False

INSTALLED_APPS = (
    'backend',
    'backend.auth_app',
)

APP_USER_MODEL = 'auth_app.User'

MIDDLEWARE_CLASSES = (
    'backend.auth_app.middlewares.TokenAuthentication',
    'backend.auth_app.middlewares.BasicAuthMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'backend.urls'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
