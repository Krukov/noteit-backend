#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime as dt


try:
    from django.core.exceptions import ImproperlyConfigured
    from django.conf import settings
    APP_LABEL = settings.APP_LABEL
except (ImportError, ImproperlyConfigured):
    DJANGO = False
    import peewee as models
    models.ForeignKey = models.ForeignKeyField
    APP_LABEL = None
else:
    DJANGO = True
    from django.db import models

from .utils import gen_key, get_alias, generate_password_hash, check_password_hash


class User(models.Model):
    """ Implement application's users. """
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=30)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(default=dt.datetime.now)
    __module__ = '__main__'  # django hack stuff

    class Meta:
        app_label = APP_LABEL
        db_table = 'user'
 
    def __unicode__(self):
        return self.username

    __str__ = __unicode__

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
            if DJANGO:
                token = Token.objects.create(user=self)
            else:
                token = Token.create(user=self)
        return token

    @classmethod
    def get(cls, username):
        if DJANGO:
            return cls.objects.filter(username=username).first()
        try:
            return cls.select().where(cls.username == username).get()
        except cls.DoesNotExist:
            return    


class NoteBook(models.Model):
    """ Implement NoteBook models"""
    name = models.CharField(max_length=2**13-1)

    __module__ = '__main__'
    
    def __unicode__(self):
        return self.name

    __str__ = __unicode__

    @classmethod
    def get_or_create(cls, name):
        if DJANGO:
            return cls.objects.get_or_create(name=name)[0]
        else:
            return cls.create_or_get(name=name)

    class Meta:
        db_table = 'notebook'
        app_label = APP_LABEL


class Note(models.Model):
    """ Implement Note models"""
    text = models.CharField(max_length=2**13-1)
    owner = models.ForeignKey(User, related_name='notes')
    alias = models.CharField(max_length=63, default=get_alias) # index=True
    active = models.BooleanField(default=True)
    created = models.DateTimeField(default=dt.datetime.now)
    notebook = models.ForeignKey(NoteBook, related_name='notes', null=True)
    __module__ = '__main__'

    class Meta:
        db_table = 'note'
        if DJANGO:
            app_label = APP_LABEL
            unique_together = ('owner', 'alias')
            ordering = ['-created']
        else:
            indexes = (
                (('owner', 'alias'), True),
            )
            order_by = ['-created']
        
    def as_dict(self):
        return {'text': self.text, 'alias': self.alias, 'notebook': getattr(self.notebook, 'name', None)}


class Token(models.Model):
    """ Store tokens for auth"""
    key = models.CharField(max_length=40, default=gen_key, primary_key=True)
    user = models.ForeignKey(User, related_name='tokens')
    created = models.DateTimeField(default=dt.datetime.now)
    __module__ = '__main__'

    class Meta:
        app_label = APP_LABEL
        db_table = 'token'

    def __unicode__(self):
        return self.key

    __str__ = __unicode__

    @classmethod
    def get_by_key(cls, key):
        try:
            if DJANGO:
                return cls.objects.select_related('user').get(key=key)
            else:
                return cls.select(cls, User).join(User).where(cls.key == key).get()  # TODO 
        except cls.DoesNotExist:  
            return


class Report(models.Model):
    """ Report for clients errors"""
    traceback = models.TextField()
    info = models.TextField()
    user = models.ForeignKey(User, null=True, related_name='reports')
    created = models.DateTimeField(default=dt.datetime.now)
    __module__ = '__main__'

    class Meta:
        if DJANGO:
            ordering = ['-created']
            app_label = APP_LABEL
        else:
            order_by = ['-created']
        db_table = 'report'

    def __unicode__(self):
        return '{} {}'.format(self.created, self.user)

    __str__ = __unicode__
