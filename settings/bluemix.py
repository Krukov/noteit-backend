import os
import json
from .settings import *

DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', None)
WSGI_APPLICATION = 'wsgi.application'

def get_pg_conf():
    config = json.loads(os.environ.get('VCAP_SERVICES'))['user-provided']
    db = [item['credentials'] for item in config if item['name'] == 'PostgreSQL']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': get_pg_conf()['username'],
        'HOST': get_pg_conf()['public_hostname'],
        'PASSWORD': get_pg_conf()['password'],
        'PORT': 5432,
    }
}

# SSL = SECURE_SSL_REDIRECT = True
# SECURE_FRAME_DENY = True
