from django import forms
from django.contrib.auth.models import User, Group
from app.models import Report, Attachment, Folder
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
        exclude = ('user', 'timeCreated','folder','groups')
    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['dateOfIncident'].widget = SelectDateWidget(years=YEAR_CHOICES)

class AttachmentForm(forms.ModelForm):
    key = forms.CharField(required=False, max_length=32, widget=forms.PasswordInput, help_text="Enter your key")
    verify_key = forms.CharField(required=False, max_length=32, widget=forms.PasswordInput, help_text="Verify the key")
    class Meta:
        model = Attachment
        exclude = ('user', 'report', 'encrypted')

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        exclude = ('user', 'slug',)

class SearchForm(forms.Form):
    shortDesc = forms.CharField(required=False, max_length=128, help_text="Short description")
    detailedDesc = forms.CharField(required=False, max_length=128, help_text="Detailed description")
    keywords = forms.CharField(required=False, max_length=128, help_text="Keywords")
    location = forms.CharField(required=False, max_length=128, help_text="Location (optional)")
    dateOfIncident = forms.DateField(required=False, widget=SelectDateWidget(years=YEAR_CHOICES), help_text="Date of incident")

class CopyMoveReportForm(forms.Form):
    #dest = forms.CharField(required=False, max_length=128, help_text="Destination (leave empty for homepage)")
    dest = forms.ModelChoiceField(required=False, queryset=None, help_text="Destination (leave empty for homepage)")

class GroupForm(forms.Form):
    name = forms.CharField(required=True, max_length=128, help_text="Group Name")

class GroupUserForm(forms.Form):
    #user = forms.CharField(required=True, max_length=128, help_text="User Name")
    user = forms.ModelChoiceField(queryset=None, help_text="User Name")


class ShareReportForm(forms.Form):
    dest = forms.ModelChoiceField(queryset=None, help_text="Group")
