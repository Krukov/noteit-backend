#!/usr/bin/python
# -*- coding: utf-8 -*

import base64

from .utils import HTTP_HEADER_ENCODING


def non_private_zone(request):
    return request.path.split('/')[1] in ['report']


def basic_auth_handler(request, auth, not_auth, set_user, user_model):
    User = user_model
    if non_private_zone(request):
        return

    if not auth or auth[0].lower() != b'basic':
        return not_auth('Not authenticated.')

    if len(auth) != 2:
        return not_auth('Invalid basic header.')

    try:
        auth_parts = base64.b64decode(auth[1]).decode(HTTP_HEADER_ENCODING).partition(':')
    except (TypeError, UnicodeDecodeError):
        return not_auth('Invalid basic header.')

    username, password = auth_parts[0], auth_parts[2]
    user = User.get(username=username)

    if user is None:
        user = User(username=username)
        user.set_password(password)
        user.save()
    else:
        if not user.check_password(password):
            return not_auth('Invalid username/password.')

        if not user.active:
            return not_auth('User inactive or deleted.')

    set_user(request, user)


def token_auth_handler(request, auth, not_auth, set_user, token_model):
    Token = token_model
    if non_private_zone(request):
        return

    if not auth or auth[0].lower() != b'token':
        return

    if len(auth) != 2:
        return not_auth('Invalid basic header.')

    try:
        key = auth[1].decode()
    except UnicodeError:
        return not_auth('Invalid token header. Token string should not contain invalid characters.')

    token = Token.get_by_key(key=key)

    if not token:
        return not_auth('Invalid token.')

    if not token.user.active:
        return not_auth('User inactive or deleted.')

    set_user(request, token.user)
