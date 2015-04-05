from django import forms
from django.contrib.auth.models import User
from app.models import Report, File
from django.forms.extras.widgets import SelectDateWidget

YEAR_CHOICES = ()
for i in range(2015,1914, -1):
    YEAR_CHOICES = YEAR_CHOICES + (str(i),)

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        exclude = ('user', 'timeCreated',)
    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['dateOfIncident'].widget = SelectDateWidget(years=YEAR_CHOICES)

class FileForm(forms.ModelForm):
    class Meta:
        model = File
        exclude = ('user', 'report',)

class SearchForm(forms.Form):
    shortDesc = forms.CharField(required=False, max_length=128, help_text="Short description")
    detailedDesc = forms.CharField(required=False, max_length=128, help_text="Detailed description")
    keywords = forms.CharField(required=False, max_length=128, help_text="Keywords")
    location = forms.CharField(required=False, max_length=128, help_text="Location (optional)")
    dateOfIncident = forms.DateField(required=False, widget=SelectDateWidget(years=YEAR_CHOICES), help_text="Date of incident")
