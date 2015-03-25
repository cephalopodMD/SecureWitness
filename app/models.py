__author__ = 'acl3qb'

from django.db import models

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128, unique=True)

    def __unicode__(self):
        return self.name

class Report(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length=128)
    body = models.TextField()

    def __unicode__(self):
        return self.title