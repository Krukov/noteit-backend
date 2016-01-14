#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime as dt

import peewee as pw
from muffin.utils import generate_password_hash, check_password_hash

from .app import app
from .utils import gen_key, get_alias


@app.ps.peewee.register
class User(pw.Model):
    """ Implement application's users. """
    username = pw.CharField(unique=True)
    password = pw.CharField()
    created = pw.DateTimeField(default=dt.datetime.now)
    active = pw.BooleanField(default=True)

    def __unicode__(self):
        return self.username

    @property
    def pk(self):
        return self.id

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(password, self.password)

    @property
    def token(self):
        try:
            token = self.tokens.get()
        except Token.DoesNotExist:
            token = Token.create(user=self)
        finally:
            return token


@app.ps.peewee.register
class Note(pw.Model):
    """ Implement Note models"""
    text = pw.TextField()
    owner = pw.ForeignKeyField(User, related_name='notes')
    alias = pw.CharField(index=True, default=get_alias)
    active = pw.BooleanField(default=True)
    created = pw.DateTimeField(default=dt.datetime.now)

    class Meta:
        indexes = (
            (('owner', 'alias'), True),
        )
        order_by = ['-created']

    def as_dict(self):
        return {'text': self.text, 'alias': self.alias}


@app.ps.peewee.register
class Token(pw.Model):
    """ Store tokens. """
    key = pw.PrimaryKeyField(default=gen_key, index=True)
    user = pw.ForeignKeyField(User, related_name='tokens')
    created = pw.DateTimeField(default=dt.datetime.now)

    def __unicode__(self):
        return self.key


@app.ps.peewee.register
class Report(pw.Model):
    traceback = pw.TextField()
    info = pw.TextField()
    user = pw.ForeignKeyField(User, null=True, related_name='reports')
    created = pw.DateTimeField(default=dt.datetime.now)

    def __unicode__(self):
        return '{} {}'.format(self.created, self.user)
