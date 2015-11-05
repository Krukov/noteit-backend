#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import include, url

from .views import NoteView, report_view
from .users import urls


urlpatterns = [
    url(r'^(?:(?P<index>\d)/)?$', NoteView.as_view()),
    url(r'^report/?$', report_view, name='report'),
    url(r'^', include(urls), name='notes'),
]