#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime as dt
import __main__

DJANGO = False
if __main__.app_type == 'django':
    DJANGO = True
    from django.db import models
else:
    import peewee as models
    models.ForeignKey = models.ForeignKeyField

if not __package__:
    __package__ = '__main__'

from utils import gen_key, get_alias, generate_password_hash, check_password_hash


class User(models.Model):
    """ Implement application's users. """
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=30)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(default=dt.datetime.now)

    __module__ = '__main__'  # django hack stuff
    class Meta:
        db_table = 'user'
 
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
            user = cls.select().where(cls.username == username).get()
        except cls.DoesNotExist:
            return    


class Note(models.Model):
    """ Implement Note models"""
    text = models.CharField(max_length=2**13-1)
    owner = models.ForeignKey(User, related_name='notes')
    alias = models.CharField(max_length=63, default=get_alias) # index=True
    active = models.BooleanField(default=True)
    created = models.DateTimeField(default=dt.datetime.now)

    __module__ = '__main__'
    class Meta:
        db_table = 'note'
        if DJANGO:
            unique_together = ('owner', 'alias')
            ordering = ['-created']
        else:
            indexes = (
                (('owner', 'alias'), True),
            )
            order_by = ['-created']
        
    def as_dict(self):
        return {'text': self.text, 'alias': self.alias}


class Token(models.Model):
    """ Store tokens for auth"""
    key = models.CharField(max_length=40, default=gen_key, primary_key=True)
    user = models.ForeignKey(User, related_name='tokens')
    created = models.DateTimeField(default=dt.datetime.now)

    __module__ = '__main__'
    class Meta:
        db_table = 'token'

    def __unicode__(self):
        return self.key

    @classmethod
    def get_by_key(cls, key):
        try:
            if DJANGO:
                return cls.objects.select_related('user').get(key=key)
            else:
                return cls.select().where(cls.key == key).get()  # TODO 
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
        else:
            order_by = ['-created']
        db_table = 'report'

    def __unicode__(self):
        return '{} {}'.format(self.created, self.user)
