import datetime
from calendar import month_name

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView

from accounts.models import Account
from api.forms import ExpenseFilterForm
from expenses.models import Expense


class ExpenseDetailView(LoginRequiredMixin, DetailView):
    model = Expense


class ExpenseCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Expense
    fields = ['name', 'amount', 'date', 'category', 'other_category', 'notes', 'account']
    success_message = 'Expense "%(name)s" Created'
    initial = {'date': datetime.date.today().strftime("%m/%d/%Y")}

    def form_valid(self, form):
        # Deduct expense balance from account
        account_object: Account = form.cleaned_data.get('account', None)
        if form.cleaned_data.get('account', None):
            account_object.balance -= form.cleaned_data.get('amount', 0)
            account_object.save()

        # Set expense owner as current user
        form.instance.owner = self.request.user

        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super(ExpenseCreateView, self).get_form(*args, **kwargs)
        form.fields['account'].queryset = Account.objects.filter(owner=self.request.user)
        return form


class ExpenseUpdateView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Expense
    fields = ['name', 'amount', 'date', 'category', 'other_category', 'notes']

    def get_success_message(self, cleaned_data):
        return f'Expense "{cleaned_data.get('name')}" Updated'

    def form_valid(self, form):
        """
        Intercepting form validation
        to update balances
        and set owner field in form

        :param form: forms.Form
        :return:
        """
        self.handle_balance_update(form)

        form.instance.owner = self.request.user
        return super().form_valid(form)

    def handle_balance_update(self, form):
        """
        Update balance of accounts currently and/or previously linked to expense.

        :param form: forms.Form
        :return: None
        """
        expense_object = self.get_object()

        # Update balances of old and new accounts
        account_object: Account = form.cleaned_data.get('account', None)
        if account_object:
            # Find difference between new and old balances, add the difference to account
            balance_diff = form.cleaned_data.get('amount', None) - expense_object.amount
            account_object.balance += balance_diff
            account_object.save()

    def test_func(self):
        return self.request.user == self.get_object().owner

    def get_form(self, *args, **kwargs):
        """
        Intercepting get_form to set the queryset for the Accounts dropdown on form

        :param args:
        :param kwargs:
        :return:
        """
        form = super(ExpenseUpdateView, self).get_form(*args, **kwargs)
        # Only include Accounts in the Account dropdown that are associated with the current user
        form.fields['account'].queryset = Account.objects.filter(owner=self.request.user)
        return form


class ExpenseDeleteView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Expense
    success_url = '/accounts/'

    def get_success_message(self, cleaned_data):
        return f'Expense "{cleaned_data.get('name')}" Deleted'

    def test_func(self):
        return self.request.user == self.get_object().owner


@login_required
def view_all_expenses(request):
    expenses = Expense.objects.filter(owner=request.user).order_by("date")
    month = None
    year = None

    if request.method == 'POST':
        form = ExpenseFilterForm(request.POST)

        if form.is_valid():
            month = form.cleaned_data.get('month', None)
            year = form.cleaned_data.get('year', None)

        else:
            messages.error(request, 'Invalid Filter Parameters')

    return view_expenses_list(request, expenses, year, month)


@login_required
def view_expenses_list(request, expenses, year=None, month=None):
    context = {
        'user': request.user.username,
        'found': False,
        'month': month,
        'year': year
    }
    if month:
        context['month'] = month_name[int(month)]
        expenses = expenses.filter(date__year=year, date__month=month)
    if year:
        expenses = expenses.filter(date__year=year)

    form = ExpenseFilterForm()

    if len(expenses) > 0:
        context['found'] = True
        context['expenses'] = expenses

        form.year = year
        form.month = month

    context['form'] = form

    return render(request, 'expenses/show_expenses.html', context)
