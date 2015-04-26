# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0003_auto_20150419_1844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='hash',
            field=models.CharField(max_length=128, blank=True),
            preserve_default=True,
        ),
    ]
