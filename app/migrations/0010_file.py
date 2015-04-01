# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20150401_1611'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('file', models.FileField(upload_to='')),
                ('encrypted', models.BooleanField(default=False, help_text='Encrypt')),
                ('report', models.ForeignKey(to='app.Report')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
