#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import url

from .views import QuestionView, drop_token

urlpatterns = [
    url(r'^(?P<uuid>[0-9a-zA-Z_-]+)/', QuestionView.as_view(), name='question'),
    url(r'^drop_token', drop_token, name='drop_token'),
]
