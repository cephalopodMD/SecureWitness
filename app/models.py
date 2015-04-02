from django.contrib.auth.models import User
from django.db import models
from SecureWitness.settings import MEDIA_ROOT
import os

def get_upload_path(instance, filename):
    return os.path.join(MEDIA_ROOT, instance.user.username, filename)

"""
class Folder(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=100)
    parentFolder = models.ForeignKey("self", blank=True)
"""

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
    user = models.ForeignKey(User)
    report = models.ForeignKey(Report)
    file = models.FileField(upload_to=get_upload_path)
    encrypted = models.BooleanField(default=False, help_text="Encrypt")

    def __str__(self):
        index = str(self.file.file).rfind('\\')
        return str(self.file.file)[index+1:]