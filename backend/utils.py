#!/usr/bin/python
# -*- coding: utf-8 -*-

import string
import random

import bleach


ALLOWED_TAGS = bleach.ALLOWED_TAGS + ['html', 'body', 'head', 'h1', 'h2', 'h3', 'h4', 'h5']
ALLOWED_STYLES = ['color']

ALLOWED_ATTRS = {}
ALLOWED_ATTRS.update(bleach.ALLOWED_ATTRIBUTES)
ALLOWED_ATTRS.update({
    '*': ['style'],
})


def clean_tags(text):
	bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, styles=ALLOWED_STYLES)


def get_random_alias(count=10):
	return ''.join(random.choice(string.ascii_lowercase) for _ in range(count))
