# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True, verbose_name=b'UUID')),
                ('text', models.TextField(max_length=16383, verbose_name=b'Message')),
                ('is_active', models.BooleanField(default=True)),
                ('date_create', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(related_name='messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date_create'],
            },
        ),
    ]
