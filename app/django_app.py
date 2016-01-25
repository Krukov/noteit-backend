#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from types import ModuleType

import ujson as json
from user_agents import parse

import django
from django.conf.urls import url
from django.core.wsgi import get_wsgi_application
from django.views.generic import View
from django.http import HttpResponse, JsonResponse, Http404
from django.forms import ModelForm
from django.views.decorators.http import require_POST
from django.db.utils import IntegrityError
from django.apps.config import AppConfig

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(BASE_DIR)

import app
__package__ = 'app'

from .utils import clean_tags, USER_AGENT_HEADER, RESERVED, HTTP_HEADER_ENCODING
from .middlewares import basic_auth_handler, token_auth_handler


APP_LABEL = __package__


class App(AppConfig):
    verbose_name = 'Main'
    label = APP_LABEL


app = App('name', sys.modules[__name__])
FILE = __file__.split('.')[-2].split('/')[-1]


class Settings(ModuleType):
    DEBUG = os.environ.get('DEBUG', 'on') == 'on'
    APP_LABEL = APP_LABEL

    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))

    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

    DATABASES = {
        'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': 'notes.db'}
    }
    ROOT_URLCONF = __name__
    MIGRATION_MODULES = {APP_LABEL: 'migrations'}
    INSTALLED_APPS = (app,)

    MIDDLEWARE_CLASSES = (
        APP_LABEL + '.' + FILE + '.TokenAuthentication',
        APP_LABEL + '.' + FILE + '.BasicAuthMiddleware',
        'django.middleware.security.SecurityMiddleware',
    )


# if "DJANGO_SETTINGS_MODULE" not in os.environ:
sys.modules['settings'] = Settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

django.setup()

from .models import Note, Report, User, Token


OTHER = 'Other'


def get_limit():
    return 50


class NoteForm(ModelForm):

    class Meta:
        model = Note
        fields = ['text', 'alias']
    
    def __init__(self, *args, **kwargs):
        super(NoteForm, self).__init__(*args, **kwargs)
        self.fields['alias'].required = False


class ReportForm(ModelForm):

    class Meta:
        model = Report
        fields = ['traceback']


def error(msg):
    return {'status': 'error', 'error': msg}


class NotesView(View):

    def get(self, request, **kwargs):
        status = 200
        limit = get_limit()
        notes = request.user.notes.filter(active=True)[:limit]
        response = [note.as_dict() for note in notes]
        if not response:
            response = error('No notes')
            status = 204
        return JsonResponse(response, status=status, safe=False)

    @staticmethod
    def post(request, **kwargs):
        status = 400
        response = error('No data')
        form = NoteForm(request.POST)
        if form.is_valid():
            status = 201
            data = form.cleaned_data
            alias = data.get('alias', None)
            if alias in RESERVED:
                status = 406
                response = error("Wrong name for alias. Reserved names are %s" % RESERVED)
            else:
                try:
                    if alias:
                        Note.objects.create(text=data['text'], owner=request.user, alias=alias)
                    else:
                        Note.objects.create(text=data['text'], owner=request.user)
                except IntegrityError:
                    status = 406
                    response = error('Alias must be unique')
                else:
                    response = {'status': 'ok'}
        return JsonResponse(response, status=status)


class NoteView(View):

    @property
    def note(self):
        alias = self.kwargs.get('alias')
        if not alias:
            raise Http404
        try:
            if alias.isdigit() and int(alias) < get_limit():
                return self.request.user.notes.filter(active=True)[int(alias) - 1]
            return self.request.user.notes.filter(alias=alias, active=True).get()
        except (Note.DoesNotExist, IndexError):
            raise Http404

    def get(self, request, **kwargs):
        response = self.note.as_dict()
        ua = parse(request.META.get(USER_AGENT_HEADER, ''))
        if ua.device.family != OTHER or ua.browser.family != OTHER:
            response = clean_tags(response['text'])
            ct = None
        else:
            response = json.dumps(response)
            ct = 'application/json'
        return HttpResponse(response, content_type=ct)

    def delete(self, request, **kwargs):
        self.note.delete()
        return JsonResponse({'status': 'ok'}, status=204)


@require_POST
def report_view(request):
    status = 400
    response = error('No data')
    form = ReportForm(request.POST)
    if form.is_valid():
        report = form.instance
        if hasattr(request, 'user') and request.user:
            report.user = request.user
        report.info = request.META.get('HTTP_USER_AGENT', '')
        report.save()
        status = 201
        response = {'status': 'ok'}
    return JsonResponse(response, status=status)


@require_POST
def get_token(request):
    return JsonResponse({'status': 'ok', 'token': request.user.token.key}, status=201)


@require_POST
def drop_token(request):
    request.user.token.delete()
    return JsonResponse({'status': 'ok'}, status=202)


urlpatterns = [
    url(r'^$', NotesView.as_view()),
    url(r'^report/?$', report_view, name='report'),
    url(r'^get_token/?', get_token, name='get_token'),
    url(r'^drop_tokens/?', drop_token, name='drop_token'),
    url(r'^(?P<alias>\w{1,30})/?$', NoteView.as_view()),
]


application = get_wsgi_application()


class BasicAuthMiddleware:
    AUTH_HEADER = 'HTTP_AUTHORIZATION'

    @classmethod
    def get_authorization(cls, request):
        auth = request.META.get(cls.AUTH_HEADER, b'')
        if isinstance(auth, type('')):
            auth = auth.encode(HTTP_HEADER_ENCODING)
        return auth.split()

    @staticmethod
    def set_user(request, user):
        request.user = user

    @staticmethod
    def not_auth(realm='', header='WWW-Authenticate'):
        response = HttpResponse(status=401)
        response[header] = realm
        return response

    @classmethod
    def not_auth_base(cls, realm):
        realm = 'Basic realm="%s"' % realm 
        return cls.not_auth(realm)

    def process_request(self, request):
        if hasattr(request, 'user'):
            return
        auth = self.get_authorization(request)
        request = basic_auth_handler(request, auth, self.not_auth_base, self.set_user, User)
        return request 


class TokenAuthentication(BasicAuthMiddleware):

    @classmethod
    def not_auth_token(cls, realm=''):
        return cls.not_auth(realm, 'Token')

    def process_request(self, request):
        if hasattr(request, 'user'):
            return
        auth = self.get_authorization(request)
        request = token_auth_handler(request, auth, self.not_auth_token, self.set_user, Token)
        return request 
        

if __name__ == "__main__":

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
