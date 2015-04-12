# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='group',
            field=models.ForeignKey(to='auth.Group', null=True, blank=True, default=None),
            preserve_default=True,
        ),
    ]
