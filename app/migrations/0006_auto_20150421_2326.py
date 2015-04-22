# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_registration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='key',
            field=models.CharField(blank=True, max_length=128, help_text='Code'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='registration',
            name='user',
            field=models.ForeignKey(help_text='Username', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
