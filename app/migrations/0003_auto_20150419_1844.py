# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_usergrouprequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='hash',
            field=models.CharField(default='NO HASH', max_length=128),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='usergrouprequest',
            name='group',
            field=models.ForeignKey(to='auth.Group', help_text='Group'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='usergrouprequest',
            name='text',
            field=models.TextField(blank=True, help_text='Reason'),
            preserve_default=True,
        ),
    ]
