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
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, digits and '
                    '@/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(r'^[\w.@+-]+$',
                                      _('Enter a valid username. '
                                        'This value may contain only letters, numbers '
                                        'and @/./+/-/_ characters.'), 'invalid'),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        })
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    is_register = models.BooleanField('registered', default=False)

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    @cached_property
    def question(self):
        question = self.questions.filter(is_active=True).last()
        if not question or not question.is_valid:
            return self.create_question()
        return question

    def create_question(self):
        questions = Question.objects.filter(is_active=True).values_list('id', flat=True)
        if questions:
            return RegisterQuestion.objects.create(user=self, question_id=random.choice(questions))

    def save(self, *args, **kwargs):
        result = super(User, self).save(*args, **kwargs)
        if self.id and not self.questions.exists():
            self.create_question()
        return result


class Question(models.Model):
    text = models.TextField(max_length=2**12-1, verbose_name='Question')
    answer = models.CharField(max_length=2**8-1, verbose_name='Answer')

    is_active = models.BooleanField(default=True)


class RegisterQuestion(models.Model):
    uuid = models.UUIDField(max_length=63, default=uuid4, unique=True, verbose_name='UUID')

    question = models.ForeignKey(Question, related_name='register_questions')
    user = models.ForeignKey(User, related_name='questions')
    is_active = models.BooleanField(default=True)

    date_create = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date_create']

    @models.permalink
    def url(self):
        return 'question', self.uuid

    @cached_property
    def is_valid(self):
        return self.date_create > timezone.now() - timedelta(getattr(settings, 'QUESTION_LIFE_TIME', {'hours': 1}))


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

    def update_key(self):
        self.key = self.generate_key()
        self.save()

    def __str__(self):
        return self.key


def get_authorization_header(request):
    HTTP_HEADER_ENCODING = 'iso-8859-1'
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, type('')):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth