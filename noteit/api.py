#!/usr/bin/python
# -*- coding: utf-8 -*-

from user_agents import parse

from .models import Note, Report, User, Token
from .app import app


OTHER = 'Other'

TEMPLATE = '{i}: {text}'


def get_limit():
	return getattr(app.config, 'MAX_NOTES', 10)

class NoteForm(Form):
    note = CharField(max_length=2**14-1)
    alias = CharField(max_length=2**6-1, required=False)


class ReportForm(ModelForm):
    class Meta:
        model = Report
        fields = ['traceback']


@app.register('/')
def notes(request):
	notes = request.user.notes.filter(is_active=True)

@app.register('/{alias}')
def note(request):
	alias = request.match_info.get('alias', 'anonymous')

class NoteView(View):

    def get(self, request, **kwargs):
        limit = self.get_limit()
        notes = request.user.notes.filter(is_active=True)

        if kwargs.get('index', None) is not None:
            response = self.get_note(notes, int(kwargs['index']) - 1)
        elif 'n' in request.GET and request.GET.get('n').isdigit():
            response = self.get_note(notes, int(request.GET['n']) - 1)
        elif 'l' in request.GET or 'last' in request.GET:
            response = notes.first().text
        elif 'a' in request.GET or 'alias' in request.GET:
            alias = request.GET.get('a', None) or request.GET.get('alias')
            note = notes.filter(alias=alias).first()
            if note:
                response = note.text
            else:
                raise Http404
        else:
            response = '\n'.join([TEMPLATE.format(i=i+1, text=note.text) for i, note in enumerate(notes[:limit])])
            if not response:
                return HttpResponse('You have not any notes. It can be created with POST request with "note" parameter at this path', status=204)

        ua = parse(request.META.get('HTTP_USER_AGENT', ''))
        if ua.device.family != OTHER or ua.browser.family != OTHER:
            response = clean_tags(response)
        return HttpResponse(response)

    def get_note(self, notes, index):
        if index + 1 >= self.get_limit() or notes.count() < index + 1:
            raise Http404
        return notes[index].text

    @staticmethod
    def post(request, **kwargs):
        form = NoteForm(request.POST)
        if form.is_valid() and not kwargs.get('index', None):
            data = form.cleaned_data
            alias = data.get('alias') if data.get('alias') else get_random_alias()
            try:
                Note.objects.create(text=data['note'], owner=request.user, alias=alias)
            except IntegrityError:
                return HttpResponse('Note with given alias ({0}) is already exists'.format(alias), status=400)
            return HttpResponse('Ok', status=201)
        return HttpResponse('Expected "note" in request body', status=400)



@require_POST
def report_view(request):
    form = ReportForm(request.POST)
    if form.is_valid():
        report = form.instance
        if hasattr(request, 'user') and request.user:
            report.user = request.user
        report.info = request.META.get('HTTP_USER_AGENT', '')
        report.save()
        return HttpResponse(status=201)
    return HttpResponse({}, status=400)
