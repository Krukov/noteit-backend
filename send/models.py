#!/usr/bin/python
# -*- coding: utf-8 -*-

from uuid import uuid4

from django.conf import settings
from django.db import models


class Note(models.Model):
    uuid = models.UUIDField(max_length=63, default=uuid4, unique=True, verbose_name='UUID')
    text = models.TextField(max_length=2**14-1, verbose_name='Note')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notes')

    is_active = models.BooleanField(default=True)

    date_create = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_create']


class Report(models.Model):
	traceback = models.TextField(max_length=2*10-1)
	info = models.TextField(max_length=2**8-1)
	user = models.ForeignKey('users.User', blank=True, null=True)

	date_create = models.DateTimeField(auto_now_add=True)

