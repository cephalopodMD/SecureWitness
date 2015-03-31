from django.contrib.auth.models import User
from django.db import models

class Report(models.Model):
    user = models.ForeignKey(User)
    timestamp = models.DateTimeField(auto_now=True)
    shortDesc = models.CharField(max_length=128)
    detailedDesc = models.CharField(max_length=128, null=True)
    # Optional location
    # Optional date of incident
    # Optional keywords
    # Optional files
    # Public or private

    def __str__(self):
        return str(self.user) + ': ' + str(self.shortDesc)