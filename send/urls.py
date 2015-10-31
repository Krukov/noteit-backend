#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import include, url

from .views import *

urlpatterns = [
    url(r'^(?:(?P<index>\d)/)?$', MessageView.as_view()),
]