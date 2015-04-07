# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='folder',
            field=models.ForeignKey(null=True, blank=True, default=None, to='app.Folder'),
            preserve_default=True,
        ),
    ]
