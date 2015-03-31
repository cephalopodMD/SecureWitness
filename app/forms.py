from django import forms
from django.contrib.auth.models import User
from app.models import Report

class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    password = forms.CharField(widget=forms.PasswordInput())

class ReportForm(forms.ModelForm):

    class Meta:
        model = Report
        exclude = ('user','timeCreated',)

    # Short description
    shortDesc = forms.CharField(max_length=128, help_text="Short description.")
    # Detailed description
    detailedDesc = forms.CharField(max_length=128, help_text="Detailed description.")
    # Optional location
    location = forms.CharField(max_length=128, help_text="Location (optional)", required=False)
    # Optional date of incident
    #dateOfIncident = forms.DateTimeField(help_text="Date of incident (optional)", required=False)