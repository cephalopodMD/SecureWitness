from django import forms
from django.contrib.auth.models import User
from app.models import Report

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class ReportForm(forms.ModelForm):
    # User - not included in form
    # Timestamp - included in form but hidden from view
    timestamp = forms.DateTimeField('Date created')
    # Short description
    shortDesc = forms.CharField(max_length=128, help_text="Please enter a short description.")
    # Detailed description
    detailedDesc = forms.CharField(max_length=128, help_text="Please enter a detailed description.")
    
    class Meta:
        model = Report
        exclude = ('user',)