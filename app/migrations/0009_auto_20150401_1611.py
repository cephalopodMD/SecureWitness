# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_attachedfiles'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attachedfiles',
            name='report',
        ),
        migrations.DeleteModel(
            name='AttachedFiles',
        ),
    ]
