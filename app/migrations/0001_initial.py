# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import app.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('file', models.FileField(upload_to=app.models.get_upload_path)),
                ('encrypted', models.BooleanField(help_text='Encrypt', default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('timeCreated', models.DateTimeField(verbose_name='Time created')),
                ('shortDesc', models.CharField(help_text='Short description', max_length=128)),
                ('detailedDesc', models.TextField(help_text='Detailed description')),
                ('location', models.CharField(help_text='Location (optional)', blank=True, max_length=128)),
                ('dateOfIncident', models.DateField(help_text='Date of incident (optional)', null=True, blank=True)),
                ('keywords', models.CharField(help_text='Keywords (optional)', blank=True, max_length=128)),
                ('private', models.BooleanField(help_text='Private', default=False)),
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
