# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_report_dateofincident'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='detailedDesc',
            field=models.TextField(help_text='Detailed description'),
            preserve_default=True,
        ),
    ]
