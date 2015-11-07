#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.views.generic import View, CreateView
from django.http import HttpResponse
from django.forms import Form, CharField, ModelForm
from django.views.decorators.http import require_POST

from .models import Note, Report

TEMPLATE = '{i}: {text}'


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
            response = notes[int(kwargs.get('index')) - 1].text
        elif 'n' in request.GET and request.GET.get('n').isdigit() and int(request.GET.get('n')) <= limit:
            response = notes[int(request.GET.get('n')) - 1].text
        elif 'l' in request.GET or 'last' in request.GET:
            response = notes[0].text
        else:
            response = '\n'.join([TEMPLATE.format(i=i+1, text=note.text) for i, note in enumerate(notes)])
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
