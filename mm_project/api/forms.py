from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from datetime import datetime
from .widgets import FengyuanChenDatePickerInput
from .models import Account, Bill, Expense
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


class ExpenseUpdateForm(forms.ModelForm):
    class Meta:
        model = Expense
        success_message = 'Expense "%(name)s" Updated'
        fields = ['name', 'amount', 'date', 'category', 'other_category', 'notes', 'account']

    def __init__(self, *args, **kwargs):
        """
        Get 'user' keyword argument and filter Account field by objects owned by the user.

        :param args: *args
        :param kwargs: **kwargs
        """
        user = kwargs.pop('user')
        super(ExpenseUpdateForm, self).__init__(*args, **kwargs)
        # self.fields['account'].queryset = Account.objects.filter(owner=user)
        # self.fields['account'].queryset = self.fields['account'].queryset.filter(owner=user)

    # Is this necessary?
    # def test_func(self):
    #     post = self.get_object()
    #     if self.request.user == post.owner:
    #         return True
    #     return False

    def form_valid(self, form):
        # self.handle_balance_update(form)
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def handle_balance_update(self, form):
        """
        Update balance of accounts currently and/or previously linked to expense.

        :param form: forms.Form
        :return: None
        """

        # Update balances of old and new accounts
        account_object: Account = form.cleaned_data.get('account', None)
        if account_object:
            if account_object == self.data_previous_account:
                """
                Case 1: New account is same as previous account
                """
                # Find difference between new and old balances, and deduct the difference from account
                balance_diff = form.cleaned_data.get('amount', None) - self.data_previous_amount
                account_object.balance -= balance_diff
                account_object.save()
            else:
                """
                Case 2: New account is not the same as previous account
                """
                # Add old amount to the previous account
                self.data_previous_account.balance += self.data_previous_amount
                self.data_previous_account.save()

                # Remove new amount from new account
                account_object.balance -= self.object.amount
                account_object.save()
        elif self.data_previous_account:
            """
            Case 3:
            Previous account exists but was removed from expense; 
            no account listed on submitted form
            """
            # Add old amount to previous account
            self.data_previous_account.balance += self.data_previous_amount
            self.data_previous_account.save()


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

    def __init__(self, *args, **kwargs):
        """
        Get 'user' keyword argument and filter Account field by objects owned by the user.

        :param args: *args
        :param kwargs: **kwargs
        """
        user = kwargs.pop('user')
        super(BillCreateForm, self).__init__(*args, **kwargs)
        self.fields['account'].queryset = Account.objects.filter(owner=user)
        self.success_message = ''

    def form_valid(self, form):
        form.instance.owner = self.request.user
        self.success_message = f'Bill "{self.pk}" Created'
        return super().form_valid(form)

    def save(self, commit=True):
        self.instance.next_due = get_next_date(self.instance.last_paid, self.instance.period)
        self.instance.owner = self.request.user

        return super(BillCreateForm).save()


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
        user = kwargs.pop('user')
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
        # form.instance.owner = self.request.user
        form.instance.next_due = get_next_date(form.instance.last_paid, form.instance.period)
        return super().form_valid(form)
