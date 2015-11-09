#!/usr/bin/python
# -*- coding: utf-8 -*-

import bleach
from user_agents import parse

from django.conf import settings
from django.views.generic import View, CreateView
from django.http import HttpResponse, Http404
from django.forms import Form, CharField, ModelForm
from django.views.decorators.http import require_POST

from .models import Note, Report


OTHER = 'Other'
TEMPLATE = '{i}: {text}'
ALLOWED_TAGS = bleach.ALLOWED_TAGS + ['html', 'body', 'head', 'h1', 'h2', 'h3', 'h4', 'h5']
ALLOWED_STYLES = ['color']

ALLOWED_ATTRS = {}
ALLOWED_ATTRS.update(bleach.ALLOWED_ATTRIBUTES)
ALLOWED_ATTRS.update({
    '*': ['style'],
})


class NoteForm(Form):
    note = CharField(max_length=2**14-1)


class ReportForm(ModelForm):

    class Meta:
        model = Report
        fields = ['traceback']


class NoteView(View):

    def get(self, request, **kwargs):
        limit = self.get_limit()
        notes = request.user.notes.filter(is_active=True)[:limit]
        if not notes:
            return HttpResponse('Hello, you have not any notes. It can be created with POST request with "note" parameter at this path', status=204)

        if 'index' in kwargs and kwargs['index'] is not None and int(kwargs['index']) <= limit:
            if len(notes) < int(kwargs['index']):
                raise Http404
            response = notes[int(kwargs.get('index')) - 1].text
        elif 'n' in request.GET and request.GET.get('n').isdigit() and int(request.GET.get('n')) <= limit:
            if len(notes) < int(request.GET.get('n')):
                raise Http404
            response = notes[int(request.GET.get('n')) - 1].text
        elif 'l' in request.GET or 'last' in request.GET:
            response = notes[0].text
        else:
            response = '\n'.join([TEMPLATE.format(i=i+1, text=note.text) for i, note in enumerate(notes)])
        ua = parse(request.META.get('HTTP_USER_AGENT', ''))
        if ua.device.family != OTHER or ua.browser.family != OTHER:
            response = bleach.clean(response, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, styles=ALLOWED_STYLES)
        return HttpResponse(response)

    @staticmethod
    def post(request, **kwargs):
        form = NoteForm(request.POST)
        if form.is_valid() and not kwargs.get('index', None):
            Note.objects.create(text=form.cleaned_data['note'], owner=request.user)
            return HttpResponse('Ok', status=201)
        return HttpResponse('Expected "note" in request body', status=400)

    @staticmethod
    def get_limit():
        return getattr(settings, 'MAX_NOTES', 5)


@require_POST
def report_view(request):
    form = ReportForm(request.POST)
    if form.is_valid():
        report = form.instance
        report.user = request.user
        report.info = request.META['HTTP_USER_AGENT']
        report.save()
        return HttpResponse(status=201)
    return HttpResponse('Invalid', status=400)
