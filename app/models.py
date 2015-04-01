from django.contrib.auth.models import User
from django.db import models

class Report(models.Model):
    timeCreated = models.DateTimeField('Time created')
    user = models.ForeignKey(User)
    shortDesc = models.CharField(max_length=128, help_text="Short description")
    detailedDesc = models.CharField(max_length=128, help_text="Detailed description")
    # Optional location
    location = models.CharField(max_length=128, blank=True, help_text="Location (optional)")
    # Optional date of incident
    dateOfIncident = models.DateField(blank=True, null=True, help_text="Date of incident (optional)")

    def __str__(self):
        return str(self.id) + ': ' + str(self.shortDesc)