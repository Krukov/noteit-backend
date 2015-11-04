#!/usr/bin/python
# -*- coding: utf-8 -*-

import base64

from django.db import transaction
from django.views.generic.detail import BaseDetailView
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.utils.functional import cached_property
from django.views.decorators.csrf import csrf_exempt

from .models import RegisterQuestion, User
from .middlewares import get_authorization_header, already_auth, HTTP_HEADER_ENCODING


class QuestionView(BaseDetailView):
    model = RegisterQuestion
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    queryset = RegisterQuestion.objects.filter(is_active=True)

    @cached_property
    def object(self):
        return self.get_object()

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        if already_auth(request):
            raise Http404
        try:
            auth = get_authorization_header(request).split()[1]
            user = base64.b64decode(auth).decode(HTTP_HEADER_ENCODING).split(':')[0]
        except (TypeError, UnicodeDecodeError):
            raise Http404
        else:
            if user != getattr(self.object.user, User.USERNAME_FIELD):
                raise Http404

        if not self.object.is_valid:
            user = self.object.user
            self.object.delete()
            return HttpResponseRedirect(user.question.url(), content='Update question')
        
        return super(QuestionView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponse(self.object.question.text)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        if 'answer' not in request.POST:
            return HttpResponse('Expect parameter "answer" in the request body. Question: "%s"' % self.object.question.text,
                                status=400)
        if self.object.question.answer == request.POST.get('answer'):
            user = self.object.user
            user.is_register = True
            self.object.is_active = False
            user.save()
            self.object.save()
            return HttpResponse('Ok', status=202)
        return HttpResponse('Wrong answer. Question: "%s"' % self.object.question.text, status=400)


@require_POST
def drop_token(request):
    request.user.auth_token.update()
    return HttpResponse(status=202)


@require_POST
def get_token(request):
    return HttpResponse(request.user.token.key, status=201)
