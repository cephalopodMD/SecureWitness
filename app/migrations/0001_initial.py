# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('timeCreated', models.DateTimeField(verbose_name='Time created')),
                ('shortDesc', models.CharField(max_length=128)),
                ('detailedDesc', models.CharField(max_length=128)),
                ('location', models.CharField(max_length=128)),
                ('dateOfIncident', models.DateField(verbose_name='Date of incident')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
