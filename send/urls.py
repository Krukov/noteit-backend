#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import include, url

from .views import NoteView, ReportView
from .users import urls


urlpatterns = [
    url(r'^(?:(?P<index>\d)/)?$', NoteView.as_view()),
    url(r'^report/?$', ReportView.as_view()),
    url(r'^', include(urls), name='notes'),
]