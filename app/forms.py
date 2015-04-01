from django import forms
from django.contrib.auth.models import User
from app.models import Report, File

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        exclude = ('user', 'timeCreated',)

class FileForm(forms.ModelForm):
    class Meta:
        model = File
        exclude = ('report',)
