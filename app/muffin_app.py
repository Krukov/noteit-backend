#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os

import muffin
import ujson as json

from peewee import IntegrityError

from asyncio import coroutine, iscoroutine
from aiohttp.web import StreamResponse, HTTPMethodNotAllowed, Response
from muffin import Response, HTTPNotFound, Handler, Application
from muffin.utils import abcoroutine


BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(os.path.normpath(BASE_DIR))
import app
__package__ = 'app'

from .middlewares import basic_auth_handler, token_auth_handler
from .utils import USER_AGENT_HEADER, OTHER, clean_tags, get_device_and_browser
from .models import Note, Report, User, Token


options = dict(
        
    PLUGINS=(
        'muffin_peewee',
    ),

    # Plugin options
    # ==============

    PEEWEE_MIGRATIONS_PATH='noteit/migrations',
    PEEWEE_CONNECTION='sqlite:///notes.db',

    DEBUGTOOLBAR_EXCLUDE=['/static'],
    DEBUGTOOLBAR_HOSTS=['0.0.0.0/0'],
    DEBUGTOOLBAR_INTERCEPT_REDIRECTS=False,
    DEBUGTOOLBAR_ADDITIONAL_PANELS=[
        'muffin_peewee',
    ],

    LOG_LEVEL='DEBUG',
)

HTTP_HEADER_ENCODING = 'iso-8859-1'
BASIC_AUTH_HEADER = 'AUTHORIZATION'


def get_authorization_header(request):
    auth = request.headers.get(BASIC_AUTH_HEADER, b'')
    if isinstance(auth, type('')):
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth.split()


def not_auth(realm='', header='WWW-Authenticate'):
    return Response(status=401, headers={header: realm})


def not_auth_base(realm):
    return not_auth('Basic realm="%s"' % realm)


def not_auth_token(realm):
    return not_auth(realm, 'Token')


def set_user(request, user):
    request.user = user


@coroutine
def baseauth_middleware_factory(app, handler):
    """ Baseauth authithication middleware factory"""
    @coroutine
    def middleware(request):
        if hasattr(request, 'user'):
            response = None
        else:
            response = basic_auth_handler(request, get_authorization_header(request),
                                          not_auth_base, set_user, User)
        if not response:
            response = yield from handler(request)

        return response
    return middleware


@coroutine
def token_middleware_factory(app, handler):
    """ Tokenbase authithication middleware factory"""
    @coroutine
    def middleware(request):
        if hasattr(request, 'user'):
            response = None
        else:
            response = token_auth_handler(request, get_authorization_header(request),
                                          not_auth_token, set_user, Token)
        if not response:
            response = yield from handler(request)
        return response
    return middleware


app = application = Application('noteit', **options)
app._middlewares.extend([token_middleware_factory, baseauth_middleware_factory])


for model in [Note, Report, User, Token]:
    app.ps.peewee.register(model)


class SuperHandler(Handler):

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


def get_limit():
    return 50


def error(msg, status=400):
    return {'status': 'error', 'error': msg}, status


@app.register('/notes')
class NotesHandler(SuperHandler):

    def get(self, request):
        limit = get_limit()
        notes = request.user.notes.filter(active=True).limit(limit)
        if not notes:
            return error('No notes', status=204)
        return [note.as_dict() for note in notes]

    def post(self, request):
        data = yield from request.post()
        if 'alias' in data:
            alias = data.get('alias')
            if alias.isdigit():
                return error("Alias can't be digit", 406)
            try:
                Note.create(text=data.get('text'), owner=request.user, alias=data.get('alias'))
            except IntegrityError:
                return error('Alias must be unique', 409)
        else:
            Note.create(text=data.get('text'), owner=request.user)
        return {'status': 'ok'}, 201


@app.register('/notes/{alias}')
class NoteHandler(SuperHandler):

    @property
    def note(self):
        alias = self.request.match_info.get('alias')
        try:
            if alias.isdigit() and int(alias) < get_limit():
                return self.request.user.notes.filter(active=True)[int(alias) - 1]
            return self.request.user.notes.filter(alias=alias, active=True).get()
        except (Note.DoesNotExist, IndexError):
            raise HTTPNotFound

    def get(self, request):
        self.request = request
        return self.note.as_dict()

    def delete(self, request):
        self.request = request
        self.note.delete_instance()
        return {'status': 'ok'}, 204


@app.register('/get_token', methods=['POST'])
def get_token_handler(request):
    return {'status': 'ok', 'token': request.user.token.key}


@app.register('/drop_tokens', methods=['POST'])
def drop_token_handler(request):
    request.user.token.delete_instance()
    return {'status': 'ok'}
