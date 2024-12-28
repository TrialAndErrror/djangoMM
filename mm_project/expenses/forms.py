from django import forms
from datetime import datetime

from accounts.models import Account


class CSVUploadForm(forms.Form):
    file = forms.FileField()
    account = forms.ModelChoiceField(queryset=Account.objects.all())


class MonthYearForm(forms.Form):
    current_year = datetime.now().year

    # Month Choices
    MONTH_CHOICES = [(i, datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)]

    # Year Choices (current year +/- 10 years)
    YEAR_CHOICES = [(year, year) for year in range(current_year - 10, current_year + 11)]

    month = forms.ChoiceField(choices=MONTH_CHOICES, required=True, label="Month")
    year = forms.ChoiceField(choices=YEAR_CHOICES, required=True, label="Year")
