import os

# Muffin
# ======

PLUGINS = (
    'muffin_peewee',
)

# Plugin options
# ==============

PEEWEE_MIGRATIONS_PATH = 'noteit/migrations'
PEEWEE_CONNECTION = 'sqlite:///local.sqlite'

DEBUGTOOLBAR_EXCLUDE = ['/static']
DEBUGTOOLBAR_HOSTS = ['0.0.0.0/0']
DEBUGTOOLBAR_INTERCEPT_REDIRECTS = False
DEBUGTOOLBAR_ADDITIONAL_PANELS = [
    'muffin_peewee',
]

# DEBUG = True
LOG_LEVEL = 'DEBUG'
