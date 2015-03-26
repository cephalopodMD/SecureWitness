from django.db import models

__author__ = 'acl3qb'

import django.db.models
from django.contrib.auth.models import User

class Report(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User)
    title = models.CharField(max_length=128)
    body = models.TextField()

    def __unicode__(self):
        return self.title

class Group(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name

class UserToGroup(models.Model):
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group)

    def __unicode__(self):
        return self.user + ' in ' + self.group