# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20150401_1245'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='keywords',
            field=models.CharField(max_length=128, blank=True, help_text='Keywords (optional)'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='report',
            name='private',
            field=models.BooleanField(default=False, help_text='Is this report private?'),
            preserve_default=False,
        ),
    ]
