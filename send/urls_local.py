#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import include, url, static
from django.contrib import admin

from .urls import urlpatterns
urlpatterns = urlpatterns + [
    url(r'^admin/', include(admin.site.urls)),
] + static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)