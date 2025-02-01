import datetime

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView
from rest_framework.reverse import reverse_lazy

from accounts.models import Account
from expenses.forms import MonthYearForm
from expenses.lookups import get_expense_categories_for_user
from expenses.models import Expense, Budget
from services.calendar import handle_calendar_scroll, get_month_choices, get_year_choices


class ExpenseDetailView(LoginRequiredMixin, DetailView):
    model = Expense


class ExpenseCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Expense
    fields = ['name', 'amount', 'date', 'category', 'notes', 'account']
    initial = {'date': datetime.date.today().strftime("%m/%d/%Y")}

    def get_success_message(self, cleaned_data):
        return f'Expense "{cleaned_data.get('name')}" Created'

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
    fields = ['name', 'amount', 'date', 'category', 'notes', 'account']

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
        form.fields['account'].queryset = Account.objects.filter(owner=self.request.user).order_by("name")
        return form


class ExpenseDeleteView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Expense
    success_url = reverse_lazy('expenses:all_expenses')

    def get_success_message(self, cleaned_data):
        return f'Expense "{cleaned_data.get('name')}" Deleted'

    def test_func(self):
        return self.request.user == self.get_object().owner


class ViewExpensesList(LoginRequiredMixin, TemplateView):
    template_name = "expenses/show_expenses.html"

    def get_initial(self):
        """Prefill the form with the current month and year."""
        current_date = datetime.datetime.now()
        return {
            'month': current_date.month,
            'year': current_date.year,
        }

    def get_context_data(self, **kwargs):
        today = datetime.date.today()
        month = kwargs.pop('month', today.month)
        year = kwargs.pop('year', today.year)

        context = super().get_context_data(**kwargs)

        context['month_choices'] = get_month_choices()
        context['year_choices'] = get_year_choices(today=today)

        context['selected_month'] = str(month)
        context['selected_year'] = str(year)

        context['expenses'] = Expense.objects.filter(
            date__month=month,
            date__year=year,
        ).order_by('date').all()
        return context

    def post(self, request, *args, **kwargs):
        """Handle POST requests to process the form."""

        year = self.request.POST.get('year')
        month = self.request.POST.get('month')
        if scroll_action := self.request.POST.get("scroll"):
            month, year = handle_calendar_scroll(
                scroll_action,
                year=year,
                month=month,
            )

        return self.render_to_response(self.get_context_data(year=year, month=month))


def handle_category_edit(request, expense):
    if request.method == 'POST':
        new_category = request.POST.get('category')
        if new_category:
            expense.category_id = new_category
            expense.save()
        context = {'expense': expense}
        return render(request, 'expenses/components/editable-category.html', context)

    all_categories = get_expense_categories_for_user(request.user)

    context = {
        'choices': all_categories,
        'selected_id': expense.category_id,
        'expense_id': expense.id,
    }

    return render(request, 'expenses/components/edit-category-inline.html', context)


def handle_budget_edit(request, expense):
    if request.method == 'POST':
        new_budget = request.POST.get('budget')
        if new_budget:
            expense.category.budget_category_id = new_budget
            expense.category.save()
        context = {'expense': expense}
        return render(request, 'expenses/components/editable-budget.html', context)

    all_budgets = Budget.objects.filter(owner=request.user).order_by("name").all()

    context = {
        'choices': all_budgets,
        'selected_id': expense.category.budget_category_id,
        'expense_id': expense.id,
    }

    return render(request, 'expenses/components/edit-budget-inline.html', context)

def edit_field_inline(request, expense_id, field):
    expense = Expense.objects.get(id=expense_id)

    if field == "category":
        return handle_category_edit(request, expense)
    if field == "budget":
        return handle_budget_edit(request, expense)

    return HttpResponseBadRequest()
