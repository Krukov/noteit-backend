#!/usr/bin/python
# -*- coding: utf-8 -*-

import binascii
import os
import random
from datetime import timedelta
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.core import validators
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(_('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, digits and '
                    '@/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(r'^[\w.@+-]{4,30}$',
                                      _('Enter a valid username. '
                                        'This value may contain only letters, numbers '
                                        'and @/./+/-/_ characters.'), 'invalid'),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        })
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    is_register = models.BooleanField('registered', default=False)

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    
    class Meta:
        verbose_name = _('app user')
        verbose_name_plural = _('app users')

    def __str__(self):
        return '{} {}'.format(self.username, ['not registered', 'registered'][self.is_register])

    @cached_property
    def question(self):
        question = self.questions.last()
        if not question or not question.is_valid:
            return self.create_question()
        return question

    @cached_property
    def token(self):
        return self.auth_token

    def drop_token(self):
        self.token.delete()
        return Token.objects.create(user=self)

    def create_question(self):
        questions = Question.objects.filter(is_active=True).values_list('id', flat=True)
        if questions:
            return RegisterQuestion.objects.create(user=self, question_id=random.choice(questions))

    def save(self, *args, **kwargs):
        first = not bool(self.id)
        result = super(User, self).save(*args, **kwargs)
        if first:
            Token.objects.create(user=self)
        if first and not self.questions.exists():
            self.create_question()
        return result


class Question(models.Model):
    text = models.TextField(max_length=2**12-1, verbose_name='Question')
    answer = models.CharField(max_length=2**8-1, verbose_name='Answer')

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return '{}: {}'.format(self.text, self.answer)


class RegisterQuestion(models.Model):
    uuid = models.UUIDField(max_length=63, default=uuid4, unique=True, verbose_name='UUID')

    question = models.ForeignKey(Question, related_name='register_questions')
    user = models.ForeignKey(User, related_name='questions')

    date_create = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date_create']

    def __str__(self):
        return '{} {}'.format(self.user.username, self.uuid)


    @models.permalink
    def url(self):
        return 'question', [self.uuid, ]

    @cached_property
    def is_valid(self):
        return self.date_create > timezone.now() - timedelta(**getattr(settings, 'QUESTION_LIFE_TIME', {'hours': 1}))


class Token(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    user = models.OneToOneField(User, related_name='auth_token')
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
