#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.views.generic import View
from django.http import HttpResponse
from django.forms import ModelForm
from django.shortcuts import redirect

from .models import Message

TEMPLATE = '{i}: {text}'


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ['text']


class MessageView(View):

    def get(self, request, *args, **kwargs):
        limit = self.get_limit()
        messages = Message.objects.filter(is_active=True, owner=request.user)[:limit]
        if not messages:
            return HttpResponse(status=204)

        if 'index' in kwargs and kwargs['index'] is not None:
            responce = messages[int(kwargs.get('index')) + 1].text
        elif 'n' in request.GET and request.GET.get('n').isdigit() and request.GET.get('n') <= limit:
            responce = messages[int(request.GET.get('n') + 1)].text
        elif 'l' in request.GET:
            responce = messages[0].text
        else:
            responce = '\n'.join([TEMPLATE.format(i=i, text=message.text) for i, message in enumerate(messages)])
        return HttpResponse(responce)

    def get_limit(self):
        return getattr(settings, 'MAX_MESSAGES', 5)

    def post(self, request, *args, **kwargs):
        form = ModelForm(request.POST)
        if form.is_valid():
            Message.object.create(text=form.clean_data['form'], owner=request.user)
            return HttpResponse(status=201)
        return HttpResponse('hi')