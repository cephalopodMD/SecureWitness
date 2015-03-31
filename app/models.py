from django.contrib.auth.models import User
from django.db import models

class Report(models.Model):
    timeCreated = models.DateTimeField('Time created')
    user = models.ForeignKey(User)
    shortDesc = models.CharField(max_length=128)
    detailedDesc = models.CharField(max_length=128)
    # Optional location
    location = models.CharField(max_length=128)
    # Optional date of incident
    #dateOfIncident = models.DateTimeField('Date of incident', blank=True, null=True, default=None)
    # Optional keywords
    # Optional files
    # Public or private

    def __str__(self):
        return str(self.user) + ': ' + str(self.shortDesc)