# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='report',
            field=models.ForeignKey(default=1, to='app.Report'),
            preserve_default=False,
        ),
    ]
