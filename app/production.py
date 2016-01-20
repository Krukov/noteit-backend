import os

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'noteit.ru').split(',')

ROOT_URLCONF = __name__
MIGRATION_MODULES = {'__main__': 'migrations'}

INSTALLED_APPS = (
    '__main__',
)

MIDDLEWARE_CLASSES = (
    'middlewares.TokenAuthentication',
    'middlewares.BasicAuthMiddleware',
    'django.middleware.security.SecurityMiddleware',
)
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', None)
WSGI_APPLICATION = 'wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PASSWORD': '',
        'PORT': 5432,
    }
}

SSL = SECURE_SSL_REDIRECT = False
SECURE_FRAME_DENY = False
