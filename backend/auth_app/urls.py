#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import url

from .views import QuestionView, drop_token, get_token


urlpatterns = [
    url(r'^question/(?P<uuid>[0-9a-zA-Z_-]+)/', QuestionView.as_view(), name='question'),
    url(r'^get_token', get_token, name='get_token'),
    url(r'^drop_token', drop_token, name='drop_token'),
]
