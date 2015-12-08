#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import include, url

from .views import NoteView, report_view
from .auth_app import urls


urlpatterns = [
    url(r'^$', NoteView.as_view()),
    url(r'^(?P<index>\d{1,2})/?$', NoteView.as_view()),
    url(r'^report/?$', report_view, name='report'),
    url(r'^', include(urls), name='notes'),
]