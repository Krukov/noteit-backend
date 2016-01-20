from .settings import *
DEBUG = TEMPLATE_DEBUG = True
SECRET_KEY = 'local'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'local.db'),
    }
}

