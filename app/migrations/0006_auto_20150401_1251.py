# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20150401_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='private',
            field=models.BooleanField(help_text='Private'),
            preserve_default=True,
        ),
    ]
