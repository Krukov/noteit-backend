#!/usr/bin/env python
import os
import sys


APPS = {
    'django': 'django_app',
    'muffin': 'muffin_app',
    'hug': 'hug_app',
}


if __name__ == "__main__":
    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] not in APPS.keys()):
        exit('pass')
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    _type = sys.argv[1]
    app_dir = os.path.join(BASE_DIR, APPS[_type])
    sys.path.append(BASE_DIR)
    import app
    __package__ = 'app'


    if _type == 'django':
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.local")
        from django.core.management import execute_from_command_line

        execute_from_command_line(sys.argv[1:]) 
