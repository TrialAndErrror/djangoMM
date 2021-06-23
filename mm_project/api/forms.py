from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from datetime import datetime


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


YEAR_CHOICES = [tuple([None, ''])] + [tuple([str(x), str(x)]) for x in range(2020, datetime.now().year + 1)]
MONTH_CHOICES = [tuple([None, ''])] + [tuple([str(x), str(x)]) for x in range(1, 13)]


class ExpenseFilterForm(forms.Form):
    year = forms.ChoiceField(choices=YEAR_CHOICES,
                             widget=forms.Select(attrs={'class': "form-select"})
                             )
    month = forms.ChoiceField(choices=MONTH_CHOICES, widget=forms.Select(attrs={'class': "form-select"}), required=False)


class BillPayForm(forms.Form):
    amount = forms.IntegerField()
    date_paid = forms.DateField()
