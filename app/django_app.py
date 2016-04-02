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
from django.views.generic import View, TemplateView
from django.http import HttpResponse, JsonResponse, Http404
from django.forms import ModelForm, CharField
from django.views.decorators.http import require_POST, require_GET
from django.db.utils import IntegrityError
from django.apps.config import AppConfig

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(BASE_DIR)

import app
__package__ = 'app'

from .utils import clean_tags, USER_AGENT_HEADER, HTTP_HEADER_ENCODING
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
        'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': os.path.join(BASE_DIR, 'notes.db')}
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

from .models import Note, Report, User, Token, NoteBook


OTHER = 'Other'


def get_limit():
    return 50


class NoteForm(ModelForm):
    _notebook = CharField(max_length=255, required=False)

    class Meta:
        model = Note
        fields = ['text', 'alias', '_notebook']
    
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

    def get_queryset(self):
        if 'all' in self.request.GET:
            return self.request.user.notes.filter(active=True)
        if 'notebook' in self.request.GET:
            return self.request.user.notes.filter(active=True,
                                                  notebook__name=self.request.GET['notebook'])[:get_limit()]
        return self.request.user.notes.filter(active=True, notebook__isnull=True)[:get_limit()]

    def get(self, request, **kwargs):
        status = 200
        notes = self.get_queryset()
        response = [note.as_dict() for note in notes]
        if not response:
            response = error('No notes')
            status = 204
        return JsonResponse(response, status=status, safe=False)

    def post(self, request, **kwargs):
        status = 400
        response = error('No data')
        form = NoteForm(request.POST)
        if form.is_valid():
            status = 201
            data = {
                'text': form.cleaned_data['text'],
                '_notebook': form.cleaned_data.get('_notebook') or kwargs.get('name'),
                'alias': form.cleaned_data.get('alias', None),
                'owner': request.user
            }

            if not data['alias']:
                del data['alias']
            if data.get('_notebook'):
                data['notebook'] = NoteBook.get_or_create(data.pop('_notebook'))
            else:
                del data['_notebook']
            try:
                Note.objects.create(**data)
            except IntegrityError:
                status = 406
                response = error('Alias must be unique, use -o option to overwrite')
            else:
                response = {'status': 'ok'}
        return JsonResponse(response, status=status)


class NotebookView(NotesView):

    def get_queryset(self):
        qs = self.request.user.notes.filter(active=True, notebook__name=self.kwargs['name'])
        return qs[:get_limit()]
    

class NoteView(View):

    @property
    def note(self):
        alias = self.kwargs.get('alias')
        if not alias:
            raise Http404
        try:
            return self.request.user.notes.filter(alias=alias, active=True).get()
        except Note.DoesNotExist:
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

    def delete(self, **kwargs):
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


@require_GET
def get_install_script(request):
    with open(os.path.join(BASE_DIR, 'install.sh')) as script:
        return HttpResponse(script.read())


urlpatterns = [
    url(r'^notes/?$', NotesView.as_view()),
    url(r'^notes/(?P<alias>.{1,30})/?$', NoteView.as_view()),
    url(r'^notebook/(?P<name>.{1,30})/?$', NotebookView.as_view()),
    
    url(r'^report/?$', report_view, name='report'),
    url(r'^get_token/?$', get_token, name='get_token'),
    url(r'^drop_tokens/?$', drop_token, name='drop_token'),

    url(r'^install\.sh$', get_install_script),
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
