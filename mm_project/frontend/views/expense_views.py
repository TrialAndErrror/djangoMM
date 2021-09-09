import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect, resolve_url
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
        form.fields['account'].queryset = Account.objects.filter(owner=self.request.user)
        return form


@login_required
def expense_update_view(request, pk):
    selected_expense = Expense.objects.get(id=pk)
    if request.method == "POST":
        form = ExpenseUpdateForm(request.POST, instance=selected_expense, user=request.user)
        if form.is_valid():
            # form.data['account'] = Account.objects.get(pk=form.cleaned_data.get('account', None))
            handle_balance_update(form, selected_expense)
            form.save()
            messages.success(request, message=f'Expense {form.cleaned_data.get("name")} updated successfully')
            return redirect(resolve_url('frontend:all_expenses'))
        else:
            messages.error(request, message=f'Expense {form.cleaned_data.get("name")} failed to update.')

    form = ExpenseUpdateForm(instance=selected_expense, user=request.user)
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