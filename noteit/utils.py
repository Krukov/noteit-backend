#!/usr/bin/python
# -*- coding: utf-8 -*-

import binascii
import os

from faker import Faker
import bleach


ALLOWED_TAGS = bleach.ALLOWED_TAGS + ['html', 'body', 'head', 'h1', 'h2', 'h3', 'h4', 'h5']
ALLOWED_STYLES = ['color']

ALLOWED_ATTRS = {}
ALLOWED_ATTRS.update(bleach.ALLOWED_ATTRIBUTES)
ALLOWED_ATTRS.update({
    '*': ['style'],
})
fake = Faker()


def gen_key():
    return binascii.hexlify(os.urandom(20)).decode()


def get_alias():
    return fake.word()


def clean_tags(text):
    return bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, styles=ALLOWED_STYLES)

