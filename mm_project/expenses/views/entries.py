import datetime
from calendar import month_name

from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, FormView
from rest_framework.reverse import reverse_lazy

from accounts.models import Account
from api.forms import ExpenseFilterForm
from expenses.forms import MonthYearForm
from expenses.models import Expense, ExpenseCategory


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
        form.fields['account'].queryset = Account.objects.filter(owner=self.request.user)
        return form


class ExpenseDeleteView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Expense
    success_url = reverse_lazy('expenses:all_expenses')

    def get_success_message(self, cleaned_data):
        return f'Expense "{cleaned_data.get('name')}" Deleted'

    def test_func(self):
        return self.request.user == self.get_object().owner


class ViewExpensesList(LoginRequiredMixin, FormView):
    template_name = "expenses/show_expenses.html"
    model = Expense
    form_class = MonthYearForm

    def get_initial(self):
        """Prefill the form with the current month and year."""
        current_date = datetime.datetime.now()
        return {
            'month': current_date.month,
            'year': current_date.year,
        }

    def get(self, request, *args, **kwargs):
        """Handle GET requests to render the form."""
        initial_data = self.get_initial()
        expenses = Expense.objects.filter(
            date__month=initial_data['month'],
            date__year=initial_data['year']
        ).all()
        form = self.get_form()
        form.set_target_url(reverse_lazy('expenses:all_expenses'))

        return render(request, self.template_name, {'form': form, 'expenses': expenses})

    def post(self, request, *args, **kwargs):
        """Handle POST requests to process the form."""
        form_class = self.get_form_class()
        form = form_class(data=request.POST)
        form.set_target_url(reverse_lazy('expenses:all_expenses'))
        context = {'form': form, 'expenses': []}
        if form.is_valid():
            context['expenses'] = Expense.objects.filter(
                date__month=form.cleaned_data['month'],
                date__year=form.cleaned_data['year']
            ).all()
            return render(request, self.template_name, context)

        return render(request, self.template_name, context, status=400)


def edit_category_inline(request, expense_id):
    expense = Expense.objects.get(id=expense_id)

    if request.method == 'POST':
        new_category = request.POST.get('category')
        expense.category_id = new_category
        expense.save()
        context = {'expense': expense}
        return  render(request, 'expenses/components/editable-category.html', context)

    all_categories = ExpenseCategory.objects.filter(expense__owner=request.user).distinct().all()

    context = {
        'choices': all_categories,
        'selected_id': expense.category_id,
        'expense_id': expense_id,
    }

    return render(request, 'expenses/components/edit-category-inline.html', context)