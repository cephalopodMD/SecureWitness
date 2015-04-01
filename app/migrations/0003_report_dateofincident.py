# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20150401_1226'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='dateOfIncident',
            field=models.DateField(null=True, help_text='Date of incident (optional)', blank=True),
            preserve_default=True,
        ),
    ]
