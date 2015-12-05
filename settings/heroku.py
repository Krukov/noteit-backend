# Parse database configuration from $DATABASE_URL
import os
import dj_database_url
from .settings import *

ALLOWED_HOSTS = ['*']
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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(asctime)s [%(process)d] [%(levelname)s] ' +
                       'pathname=%(pathname)s lineno=%(lineno)s ' +
                       'funcname=%(funcName)s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
    }
}