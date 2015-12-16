#!/usr/bin/python
# -*- coding: utf-8 -*-

from muffin import Handler, Response
from user_agents import parse

from .models import Note, Report
from .app import app


OTHER = 'Other'

TEMPLATE = '{i}: {text}'


def get_limit():
    # return getattr(app.config, 'MAX_NOTES', 10)
    return 10


@app.register('/')
class NotesHandler(Handler):

    def get(self, request):
        limit = get_limit()
        notes = request.user.notes.filter(active=True).limit(limit)
        return [{'alias': note.alias, 'text': note.text} for note in notes]

    def post(self, request):
        data = yield from request.post()
        note = Note.create(text=data.get('text'), alias=data.get('alias', None))
        return Response({'status': 'ok'}, status=204)


@app.register('/{alias}')
class NoteHandler(Handler):

    @property
    def note(self):
        alias = self.request.match_info.get('alias')
        return request.user.notes.filter(alias=alias, active=True).get()
        
    def get(self, request):
        note = self.note
        return {'alias': note.alias, 'text': note.text}

    def post(self, request):
        data = yield from request.post()    
        note = self.note
        note.alias = data.get('alias', note.alias)
        note.text = data.get('text', note.text)
        return Response({'status': 'ok'}, status=200)


@app.register('/report', methods=['POST'])
def report_view(request):
    data = yield from request.post()
    if 'traceback' in data: 
        report = Report(traceback=data.get('traceback'))
        if hasattr(request, 'user') and request.user:
            report.user = request.user
        report.info = request.META.get('HTTP_USER_AGENT', '')
        report.save()
        return HttpResponse(status=201)
    return HttpResponse({}, status=400)
