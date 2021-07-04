import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView

from api.models import Expense, Account
from api.forms import ExpenseFilterForm
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
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_form(self, *args, **kwargs):
        form = super(ExpenseCreateView, self).get_form(*args, **kwargs)
        form.fields['account'].queryset = Account.objects.filter(owner=self.request.user)
        return form



class ExpenseUpdateView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Expense
    fields = ['name', 'amount', 'date', 'category', 'other_category', 'notes', 'account']
    success_message = 'Expense "%(name)s" Updated'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.owner:
            return True
        return False

    def get_form(self, *args, **kwargs):
        form = super(ExpenseUpdateView, self).get_form(*args, **kwargs)
        form.fields['account'].queryset = Account.objects.filter(owner=self.request.user)
        return form


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
