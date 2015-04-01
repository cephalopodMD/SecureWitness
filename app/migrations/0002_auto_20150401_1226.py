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
            name='detailedDesc',
            field=models.CharField(max_length=128, help_text='Detailed description'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='report',
            name='location',
            field=models.CharField(max_length=128, blank=True, help_text='Location (optional)'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='report',
            name='shortDesc',
            field=models.CharField(max_length=128, help_text='Short description'),
            preserve_default=True,
        ),
    ]
