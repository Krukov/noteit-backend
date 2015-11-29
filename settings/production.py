import os
from .settings import *

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

QUESTION_LIFE_TIME = {'seconds': 20}
MAX_NOTES = 10