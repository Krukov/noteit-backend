#!/usr/bin/python
# -*- coding: utf-8 -*-

from muffin import Response, HTTPNotFound
from schematics.types import StringType
from peewee import IntegrityError

from .utils import SuperHandeler as Handler, USER_AGENT_HEADER
from .models import Note, Report
from .app import app


RESERVED = ['get_token', 'drop_token', 'report']


def get_limit():
    return 50


def error(msg, status=400):
    return {'status': 'error', 'error': msg}, status


@app.register('/')
class NotesHandler(Handler):

    def get(self, request):
        limit = get_limit()
        notes = request.user.notes.filter(active=True).limit(limit)
        if not notes:
            return error('No notes', status=204)
        return [{'alias': note.alias, 'text': note.text} for note in notes]

    def post(self, request):
        data = yield from request.post()
        if 'alias' in data:
            alias = data.get('alias')
            if alias.isdigit():
                return error("Alias can't be digit", 406)
            elif alias in RESERVED:
                return error("wrong name for alias. Reserved names are %s" % RESERVED, 406)
            try:
                Note.create(text=data.get('note'), owner=request.user, alias=data.get('alias'))
            except IntegrityError:
                return error('Alias must be unique', 409)
        else:
            Note.create(text=data.get('note'), owner=request.user)
        return {'status': 'ok'}, 201


@app.register('/report', methods=['POST'])
def report_view(request):
    data = yield from request.post()
    if 'traceback' in data:
        report = Report(traceback=data.get('traceback'))
        if hasattr(request, 'user') and request.user:
            report.user = request.user
        report.info = request.headers.get(USER_AGENT_HEADER, b'')
        report.save()
        return {'status': 'ok'}
    return error('required traceback')[0]


@app.register('/get_token', methods=['POST'])
def get_token_handler(request):
    return {'status': 'ok', 'token': request.user.token.key}


@app.register('/drop_token', methods=['POST'])
def drop_token_handler(request):
    request.user.token.delete_instance()
    return {'status': 'ok'}


@app.register('/{alias}')
class NoteHandler(Handler):

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
        note = self.note
        return {'alias': note.alias, 'text': note.text}

    def delete(self, request):
        self.request = request
        self.note.delete_instance()
        return {'status': 'ok'}, 204
