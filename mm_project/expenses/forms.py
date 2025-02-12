from crispy_forms.templatetags.crispy_forms_field import classes
from django import forms
from datetime import datetime

from rest_framework.reverse import reverse_lazy

from accounts.models import Account
from expenses.models import Expense, ExpenseCategory


class CSVUploadForm(forms.Form):
    file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
    )
    account = forms.ModelChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        queryset=Account.objects.all()
    )


class MonthYearForm(forms.Form):
    current_year = datetime.now().year

    # Month Choices
    MONTH_CHOICES = [(i, datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)]

    # Year Choices (current year +/- 10 years)
    YEAR_CHOICES = [(year, year) for year in range(current_year - 10, current_year + 11)]

    month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        required=True,
        label="Month",
        widget=forms.Select(
            attrs={
                'hx-trigger': 'load,change',
                'hx-target': '#budget-content',
                'hx-select': '#budget-content',
                'hx-post': reverse_lazy('expenses:reports_monthly'),
                'class': 'form-control'
            }
        ),

    )
    year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        required=True,
        label="Year",
        widget=forms.Select(
            attrs={
                'hx-trigger': 'change',
                'hx-post': reverse_lazy('expenses:reports_monthly'),
                'class': 'form-control'
            }
        ),
    )

    def set_target_url(self, url):
        self.fields['month'].widget.attrs['hx-post'] = url
        self.fields['year'].widget.attrs['hx-post'] = url


class ExpenseUpdateForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['name', 'amount', 'date', 'category', 'notes', 'account']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ExpenseCategory.objects.order_by('name')
