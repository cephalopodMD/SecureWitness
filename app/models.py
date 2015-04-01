from django.contrib.auth.models import User
from django.db import models

class Report(models.Model):
    timeCreated = models.DateTimeField('Time created')
    user = models.ForeignKey(User)
    shortDesc = models.CharField(max_length=128, help_text="Short description")
    detailedDesc = models.TextField(help_text="Detailed description")
    # Optional location
    location = models.CharField(max_length=128, blank=True, help_text="Location (optional)")
    # Optional date of incident
    dateOfIncident = models.DateField(blank=True, null=True, help_text="Date of incident (optional)")
    # Optional keywords
    keywords = models.CharField(max_length=128, blank=True, help_text="Keywords (optional)")
    # Indicates whether the report is private or public
    private = models.BooleanField(default=False, help_text="Private")

    def __str__(self):
        return str(self.id) + ': ' + str(self.shortDesc)

class File(models.Model):
    report = models.ForeignKey(Report)
    file = models.FileField(upload_to="")
    encrypted = models.BooleanField(default=False, help_text="Encrypt")