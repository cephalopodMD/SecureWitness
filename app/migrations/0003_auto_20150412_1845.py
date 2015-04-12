# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('app', '0002_report_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='group',
        ),
        migrations.AddField(
            model_name='report',
            name='groups',
            field=models.ManyToManyField(blank=True, default=None, to='auth.Group', null=True),
            preserve_default=True,
        ),
    ]
