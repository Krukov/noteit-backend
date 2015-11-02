#!/usr/bin/python
# -*- coding: utf-8 -*

import base64

from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import SimpleLazyObject
from django.shortcuts import redirect

from .models import Token, User


HTTP_HEADER_ENCODING = 'iso-8859-1'
BASIC_AUTH_HEADER = 'HTTP_AUTHORIZATION'


def get_authorization_header(request):
    auth = request.META.get(BASIC_AUTH_HEADER, b'')
    if isinstance(auth, type('')):
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth

def is_privete_zone(request):
    return request.path in ['/', '/drop_token']    


def allready_auth(request):
    return hasattr(request, 'user') and hasattr(request.user, 'pk') and request.user.pk


class BasicAuthMiddleware:

    @staticmethod
    def not_auth(realm=''):
        response = HttpResponse(status=401)
        response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
        return response

    def process_request(self, request):
        if not is_privete_zone(request) or allready_auth(request):
            return

        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'basic':
            return self.not_auth(_('Not authenticated.'))
 

        if len(auth) != 2:
            return self.not_auth(_('Invalid basic header.'))

        try:
            auth_parts = base64.b64decode(auth[1]).decode(HTTP_HEADER_ENCODING).partition(':')
        except (TypeError, UnicodeDecodeError):
            return self.not_auth(_('Invalid basic header.'))

        user, password = auth_parts[0], auth_parts[2]
        credentials = {
            User.USERNAME_FIELD: user,
            'password': password
        }
        user, created = User.objects.get_or_create(**{User.USERNAME_FIELD: user})
        if created:
            user.set_password(password)
            return redirect(user.question.url())

        user = authenticate(**credentials)  # TODO: remake with yourown logic

        if user is None:
            return self.not_auth(_('Invalid username/password.'))

        if not user.is_active:
            return self.not_auth(_('User inactive or deleted.'))

        if not user.is_register:
            return redirect(user.question.url())

        request.user = user


class TokenAuthentication:

    @staticmethod
    def not_auth(realm=''):
        response = HttpResponse(status=401)
        response['Token'] = realm
        return response

    def process_request(self, request):
        if not is_privete_zone(request) or allready_auth(request):
            return

        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'token':
            return

        if len(auth) != 2:
            return self.not_auth(_('Invalid basic header.'))

        try:
            key = auth[1].decode()
        except UnicodeError:
            return self.not_auth(_('Invalid token header. Token string should not contain invalid characters.'))

        try:
            token = Token.objects.select_related('user').get(key=key)
        except Token.DoesNotExist:
            return self.not_auth(_('Invalid token.'))

        if not token.user.is_active:
            return self.not_auth(_('User inactive or deleted.'))

        request.user = token.user
        
        if not token.user.is_register:
            return redirect(token.user.question.url())
