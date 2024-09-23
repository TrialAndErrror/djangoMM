from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from datetime import datetime
from .widgets import FengyuanChenDatePickerInput
from bills.models import PERIOD_CHOICES, Bill
from accounts.models import Account
from api.tools import get_next_date


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
    month = forms.ChoiceField(choices=MONTH_CHOICES, widget=forms.Select(attrs={'class': "form-select"}),
                              required=False)


class BillPayForm(forms.Form):
    amount = forms.DecimalField()
    date_paid = forms.DateField(
        widget=FengyuanChenDatePickerInput()
    )


class BillCreateForm(forms.ModelForm):
    """
    Custom form for Bills Create.

    Required to implement functionality limiting choices of Account dropdown to only Accounts owned
    by the currently logged-in user.
    """
    class Meta:
        model = Bill
        fields = ['name', 'amount', 'variable', 'last_paid', 'period', 'account']
        success_message = 'Bill "%(name)s" Created'
        widgets = {
            'last_paid': FengyuanChenDatePickerInput
        }


class BillUpdateForm(forms.ModelForm):
    """
    Custom form for Bills Update.

    Required to implement functionality limiting choices of Account dropdown to only Accounts owned
    by the currently logged-in user.
    """
    class Meta:
        model = Bill
        fields = ['name', 'amount', 'variable', 'last_paid', 'period', 'account']
        success_message = 'Bill "%(name)s" Updated'

    def __init__(self, *args, **kwargs):
        """
        Get 'user' keyword argument and filter Account field by objects owned by the user.

        :param args: *args
        :param kwargs: **kwargs
        """
        super(BillUpdateForm, self).__init__(*args, **kwargs)
        self.fields['account'].queryset = Account.objects.filter(owner=user)

    def form_valid(self, form):
        """
        On validation, set the owner to the current user
        and set the next due date based on get_next_date function.

        Then continue validation.

        :param form:
        :return:
        """
        form.instance.owner = self.request.user
        form.instance.next_due = get_next_date(form.instance.last_paid, form.instance.period)
        return super().form_valid(form)
