#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import transaction
from django.views.generic.detail import BaseDetailView
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import RegisterQuestion


class QuestionView(BaseDetailView):
    model = RegisterQuestion
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    queryset = RegisterQuestion.objects.filter(is_active=True)

    def get(self, request, *args, **kwargs):
        _object = self.get_object()
        if not _object.is_valid:
            raise Http404
        return HttpResponse(_object.question.text)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        _object = self.get_object()
        if not _object.is_valid:
            raise Http404
        if 'answer' in request.POST:
            if _object.question.answer == request.POST.get('answer'):
                user = _object.user
                user.is_register = True
                _object.is_active = False
                user.save()
                _object.save()
                return HttpResponse('Ok', status=202)
            return HttpResponse('Wrong answer. Question: "%s"' % _object.question.text, status=400)
        return HttpResponse('Expect parameter "answer" in the request body. Question: "%s"' % _object.question.text,
                            status=400)


@login_required
@require_POST
def drop_token(request):
    request.user.auth_token.update()
    return HttpResponse(status=202)
