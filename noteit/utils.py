#!/usr/bin/python
# -*- coding: utf-8 -*-

import binascii
import os

import bleach
import ujson as json
from faker import Faker
from user_agents import parse

from asyncio import coroutine, iscoroutine
from aiohttp.multidict import MultiDict, MultiDictProxy
from aiohttp.web import StreamResponse, HTTPMethodNotAllowed, Response

from muffin import Handler
from muffin.utils import to_coroutine, abcoroutine



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
BLOCKED_ALIAS = ['last', 'report']

USER_AGENT_HEADER = 'User-Agent'
OTHER = 'Other'
TEMPLATE = '{n.alias}: {n.text}'


def gen_key():
    return binascii.hexlify(os.urandom(20)).decode()


def get_alias():
    alias = fake.word()
    if alias in BLOCKED_ALIAS:
        return get_alias()
    return alias


def clean_tags(text):
    return bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, styles=ALLOWED_STYLES)


def get_device_and_browser(request):
    ua = parse(request.headers.get(USER_AGENT_HEADER, b''))
    return ua.device.family, ua.browser.family


class SuperHandeler(Handler):

    @abcoroutine
    def make_response(self, request, response):
        while iscoroutine(response):
            response = yield from response

        status = 200

        if not response:
            response = ''
            status = 204

        if isinstance(response, (list, tuple)):
            if len(response) == 2 and isinstance(response[1], int):
                response, status = response

        if isinstance(response, (dict, )):
            device, browser = get_device_and_browser(request)
            if device != OTHER or browser != OTHER:
                response = clean_tags(response['text'])

        if isinstance(response, str):
            response = Response(text=response, content_type='text/html', charset=self.app.cfg.ENCODING)

        elif isinstance(response, (list, tuple, dict)):
            response = Response(text=json.dumps(response), content_type='application/json')

        elif isinstance(response, bytes):
            response = Response(body=response, content_type='text/html', charset=self.app.cfg.ENCODING)

        response.set_status(status)
        return response
