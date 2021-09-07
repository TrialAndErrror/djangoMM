import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.views.generic import DetailView, CreateView, DeleteView

from api.models import Expense, Account
from api.forms import ExpenseFilterForm, ExpenseUpdateForm
from django.contrib import messages

from calendar import month_name


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
        form.fields['account'].choices = Account.objects.filter(owner=self.request.user)
        return form


@login_required
def expense_update_view(request, pk):
    selected_expense = Expense.objects.get(id=pk)
    if request.method == "POST":
        form = ExpenseUpdateForm(request.POST, instance=selected_expense, user=request.user)
        if form.is_valid():
            handle_balance_update(form, selected_expense)
            form.save()

    form = ExpenseUpdateForm(user=request.user)
    return render(request, "api/expense_form.html", {"form": form})


def handle_balance_update(form, selected_expense):
    account_object: Account = form.cleaned_data.get('account', None)
    if account_object:
        if account_object == selected_expense.account:
            """
            Case 1: New account is same as previous account
            """
            balance_diff = form.cleaned_data.get('amount', None) - selected_expense.account.balance
            account_object.balance -= balance_diff
            account_object.save()
        else:
            """
            Case 2: New account is not the same as previous account
            """
            # Add old amount to the previous account
            selected_expense.account.balance += selected_expense.amount
            selected_expense.account.save()

            # Remove new amount from new account
            account_object.balance -= form.cleaned_data.get('amount', None)
            account_object.save()
    elif selected_expense.account:
        """
        Case 3:
        Previous account exists but was removed from expense; 
        no account listed on submitted form
        """
        # Add old amount to previous account
        selected_expense.account.balance += selected_expense.amount
        selected_expense.account.save()


# class ExpenseUpdateView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#     model = Expense
#     fields = ['name', 'amount', 'date', 'category', 'other_category', 'notes', 'account']
#     success_message = 'Expense "%(name)s" Updated'
#
#     def get_object(self):
#         obj = super().get_object()
#
#         # Get previous expense amount
#         self.data_previous_amount = obj.amount
#
#         # Get previous expense account
#         self.data_previous_account = obj.account
#
#         return obj
#
#     def form_valid(self, form):
#         """
#         Intercepting form validation
#         to update balances
#         and set owner field in form
#
#         :param form: forms.Form
#         :return:
#         """
#         self.handle_balance_update(form)
#
#         form.instance.owner = self.request.user
#         return super().form_valid(form)
#
#     def handle_balance_update(self, form):
#         """
#         Update balance of accounts currently and/or previously linked to expense.
#
#         :param form: forms.Form
#         :return: None
#         """
#
#         # Update balances of old and new accounts
#         account_object: Account = form.cleaned_data.get('account', None)
#         if account_object:
#             if account_object == self.data_previous_account:
#                 """
#                 Case 1: New account is same as previous account
#                 """
#                 # Find difference between new and old balances, and deduct the difference from account
#                 balance_diff = form.cleaned_data.get('amount', None) - self.data_previous_amount
#                 account_object.balance -= balance_diff
#                 account_object.save()
#             else:
#                 """
#                 Case 2: New account is not the same as previous account
#                 """
#                 # Add old amount to the previous account
#                 self.data_previous_account.balance += self.data_previous_amount
#                 self.data_previous_account.save()
#
#                 # Remove new amount from new account
#                 account_object.balance -= self.object.amount
#                 account_object.save()
#         elif self.data_previous_account:
#             """
#             Case 3:
#             Previous account exists but was removed from expense;
#             no account listed on submitted form
#             """
#             # Add old amount to previous account
#             self.data_previous_account.balance += self.data_previous_amount
#             self.data_previous_account.save()
#
#     def test_func(self):
#         post = self.get_object()
#         if self.request.user == post.owner:
#             return True
#         return False
#
#     def get_form(self, *args, **kwargs):
#         """
#         Intercepting get_form to set the queryset for the Accounts dropdown on form
#
#         :param args:
#         :param kwargs:
#         :return:
#         """
#         form = super(ExpenseUpdateView, self).get_form(*args, **kwargs)
#         # Only include Accounts in the Account dropdown that are associated with the current user
#         form.fields['account'].queryset = Account.objects.filter(owner=self.request.user)
#         return form


class ExpenseDeleteView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Expense
    success_url = '/accounts/'
    success_message = 'Expense "%(name)s" Deleted'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.owner:
            return True
        return False


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

    return render(request, 'frontend/expenses/show_expenses.html', context)