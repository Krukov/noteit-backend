#!/usr/bin/python
# -*- coding: utf-8 -*-

from uuid import uuid4

from django.conf import settings
from django.db import models


class Note(models.Model):
    text = models.TextField(max_length=2**14-1, verbose_name='Note')
    owner = models.ForeignKey(settings.APP_USER_MODEL, related_name='notes')
    alias = models.CharField(max_length=2**6-1, blank=True, null=True)

    is_active = models.BooleanField(default=True)

    date_create = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('owner', 'alias')
        ordering = ['-date_create']
        db_table = 'note'


class Report(models.Model):
    traceback = models.TextField(max_length=2**10-1)
    info = models.TextField(max_length=2**8-1)
    user = models.ForeignKey(settings.APP_USER_MODEL, blank=True, null=True)

    date_create = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_create']
        db_table = 'report'

    def __str__(self):
        return '{} {}'.format(self.date_create, self.info)

