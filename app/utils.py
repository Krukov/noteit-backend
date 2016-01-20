#!/usr/bin/python
# -*- coding: utf-8 -*-

import binascii
import os

import bleach
import ujson as json
from faker import Faker
from user_agents import parse

from muffin.utils import generate_password_hash, check_password_hash



ALLOWED_TAGS = bleach.ALLOWED_TAGS + ['html', 'body', 'head', 'h1', 'h2', 'h3', 'h4', 'h5', 'pre',
                                      'meta', 'title', 'div', 'span', 'input', 'label', 'form', 'time',
                                      'img', 'button', 'tr', 'td', 'table', 'tbody', 'p', 'hr', 'br', 'nav']
ALLOWED_STYLES = ['color']

ALLOWED_ATTRS = {}
ALLOWED_ATTRS.update(bleach.ALLOWED_ATTRIBUTES)
ALLOWED_ATTRS.update({
    '*': ['style'],
})
fake = Faker()

RESERVED = ['get_token', 'drop_token', 'report']
HTTP_HEADER_ENCODING = 'iso-8859-1'
USER_AGENT_HEADER = 'User-Agent'
OTHER = 'Other'
TEMPLATE = '{n.alias}: {n.text}'


def gen_key():
    return binascii.hexlify(os.urandom(20)).decode()


def get_alias():
    alias = fake.word()
    if alias in RESERVED:
        return get_alias()
    return alias


def clean_tags(text):
    return bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, styles=ALLOWED_STYLES)


def get_device_and_browser(request):
    ua = parse(request.headers.get(USER_AGENT_HEADER, b''))
    return ua.device.family, ua.browser.family
