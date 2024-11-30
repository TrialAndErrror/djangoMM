from django import forms

from accounts.models import Account


class CSVUploadForm(forms.Form):
    file = forms.FileField()
    account = forms.ModelChoiceField(queryset=Account.objects.all())
