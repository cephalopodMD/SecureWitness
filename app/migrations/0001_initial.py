# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import app.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, help_text='Folder Name')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('timeCreated', models.DateTimeField(verbose_name='Time created')),
                ('shortDesc', models.CharField(max_length=128, help_text='Short description')),
                ('detailedDesc', models.TextField(help_text='Detailed description')),
                ('location', models.CharField(max_length=128, blank=True, help_text='Location (optional)')),
                ('dateOfIncident', models.DateField(blank=True, null=True, help_text='Date of incident (optional)')),
                ('keywords', models.CharField(max_length=128, blank=True, help_text='Keywords (optional)')),
                ('private', models.BooleanField(default=False, help_text='Private')),
                ('folder', models.ForeignKey(blank=True, to='app.Folder', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='folder',
            unique_together=set([('user', 'name')]),
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
