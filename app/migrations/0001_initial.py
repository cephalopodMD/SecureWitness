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
            name='File',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('file', models.FileField(upload_to='')),
                ('encrypted', models.BooleanField(default=False, help_text='Encrypt')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('timeCreated', models.DateTimeField(verbose_name='Time created')),
                ('shortDesc', models.CharField(max_length=128, help_text='Short description')),
                ('detailedDesc', models.TextField(help_text='Detailed description')),
                ('location', models.CharField(max_length=128, blank=True, help_text='Location (optional)')),
                ('dateOfIncident', models.DateField(blank=True, help_text='Date of incident (optional)', null=True)),
                ('keywords', models.CharField(max_length=128, blank=True, help_text='Keywords (optional)')),
                ('private', models.BooleanField(default=False, help_text='Private')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='file',
            name='report',
            field=models.ForeignKey(to='app.Report'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='file',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
