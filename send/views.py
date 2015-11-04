#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.views.generic import View, CreateView
from django.http import HttpResponse
from django.forms import Form, CharField

from .models import Note, Report

TEMPLATE = '{i}: {text}'


class NoteForm(Form):
    note = CharField(max_length=2**14-1)


class NoteView(View):

    def get(self, request, *args, **kwargs):
        limit = self.get_limit()
        notes = request.user.notes.filter(is_active=True)[:limit]
        if not notes:
            return HttpResponse(status=204)

        if 'index' in kwargs and kwargs['index'] is not None and int(kwargs['index']) <= limit:
            responce = notes[int(kwargs.get('index')) + 1].text
        elif 'n' in request.GET and request.GET.get('n').isdigit() and int(request.GET.get('n')) <= limit:
            responce = notes[int(request.GET.get('n')) - 1].text
        elif 'l' in request.GET or 'last' in request.GET:
            responce = notes[0].text
        else:
            responce = '\n'.join([TEMPLATE.format(i=i+1, text=note.text) for i, note in enumerate(notes)])
        return HttpResponse(responce)

    def post(self, request, *args, **kwargs):
        form = NoteForm(request.POST)
        if form.is_valid() and not kwargs.get('index', None):
            Note.objects.create(text=form.cleaned_data['note'], owner=request.user)
            return HttpResponse(status=201)
        return HttpResponse('Expected "note" in request body', status=400)

    @staticmethod
    def get_limit():
        return getattr(settings, 'MAX_NOTES', 5)


class ReportView(CreateView):
    model = Report

    