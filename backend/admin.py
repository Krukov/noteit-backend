#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib.admin import register, ModelAdmin
from . import models
from .auth_app.models import Token, User, Question, RegisterQuestion


@register(models.Report)
class ReportAdmin(ModelAdmin):
    pass


@register(models.Note)
class NoteAdmin(ModelAdmin):
    pass


@register(User)
class UserAdmin(ModelAdmin):
    pass


@register(Question)
class QuestionAdmin(ModelAdmin):
    pass


@register(Token)
class TokenAdmin(ModelAdmin):
    pass


@register(RegisterQuestion)
class RegisterQuestionAdmin(ModelAdmin):
    pass