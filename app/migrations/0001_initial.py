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
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('file', models.FileField(upload_to=app.models.get_upload_path)),
                ('encrypted', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(help_text='Folder Name', max_length=128)),
                ('slug', models.SlugField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('timeCreated', models.DateTimeField(verbose_name='Time created')),
                ('shortDesc', models.CharField(help_text='Short description', max_length=128)),
                ('detailedDesc', models.TextField(help_text='Detailed description')),
                ('location', models.CharField(help_text='Location (optional)', max_length=128, blank=True)),
                ('dateOfIncident', models.DateField(null=True, help_text='Date of incident (optional)', blank=True)),
                ('keywords', models.CharField(help_text='Keywords (optional)', max_length=128, blank=True)),
                ('private', models.BooleanField(default=False, help_text='Private')),
                ('folder', models.ForeignKey(null=True, default=None, blank=True, to='app.Folder')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='attachment',
            name='report',
            field=models.ForeignKey(to='app.Report'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='attachment',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
