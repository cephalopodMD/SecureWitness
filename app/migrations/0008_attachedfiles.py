# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20150401_1535'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttachedFiles',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to='')),
                ('encrypted', models.BooleanField(default=False, help_text='Encrypt')),
                ('report', models.ForeignKey(to='app.Report')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
