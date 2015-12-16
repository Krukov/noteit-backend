#!/usr/bin/python
# -*- coding: utf-8 -*-

import asyncio
import base64

from muffin import Response

HTTP_HEADER_ENCODING = 'iso-8859-1'
BASIC_AUTH_HEADER = 'AUTHORIZATION'


def get_authorization_header(request):
    auth = request.headers.get(BASIC_AUTH_HEADER, b'')
    if isinstance(auth, type('')):
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


def non_privat_zone(request):
    return request.path.split('/')[1] in ['admin', 'question', 'report']


def not_auth(realm='', header='WWW-Authenticate'):
    return Response(status=401, headers={header: realm})


def not_auth_base(realm):
    return not_auth('Basic realm="%s"' % realm)

def not_auth_token(realm):
    return not_auth(realm, 'Token')


@asyncio.coroutine
def baseauth_middleware_factory(app, handler):
    """ Baseauth authithication middleware factory"""
    from .models import User

    @asyncio.coroutine
    def middleware(request):
        if not non_privat_zone(request) and not hasattr(request, 'user'):

            auth = get_authorization_header(request).split()
            if not auth or auth[0].lower() != b'basic':
                return not_auth_base('Not authithicate')

            if len(auth) != 2:
                return not_auth_base('Invalid basic header.')

            try:
                auth_parts = base64.b64decode(auth[1]).decode(HTTP_HEADER_ENCODING).partition(':')
            except (TypeError, UnicodeDecodeError):
                return not_auth_base('Invalid basic header.')

            username, password = auth_parts[0], auth_parts[2]
            try:
                user = User.select().where(User.username == username).get()
            except User.DoesNotExist:
                user = User(username=username)
                user.set_password(password)
                user.save()
            else:
                if not user.check_password(password):
                    return not_auth_base('Invalid username/password.')

                if not user.active:
                    return not_auth_base('User inactive or deleted.')

            request.user = user

        response = yield from handler(request)
        return response

    return middleware


@asyncio.coroutine
def token_middleware_factory(app, handler):
    """ Tokenbase authithication middleware factory"""
    from .models import Token


    @asyncio.coroutine
    def middleware(request):
        if not non_privat_zone(request) and not hasattr(request, 'user'):

            auth = get_authorization_header(request).split()

            if not auth or auth[0].lower() != b'token':
                return not_auth_token('Not authenticated.')

            if len(auth) != 2:
                return not_auth_token('Invalid basic header.')

            try:
                key = auth[1].decode()
            except UnicodeError:
                return not_auth_token('Invalid token header. Token string should not contain invalid characters.')
            try:
                token = Token.select().where(Token.key == key).get()
            except Token.DoesNotExist:
                return not_auth_token(_('Invalid token.'))

            if not token.user.active:
                return not_auth_token(_('User inactive or deleted.'))

            request.user = token.user

        response = yield from handler(request)
        return response


    return middleware

