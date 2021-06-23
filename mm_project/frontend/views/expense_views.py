from calendar import month_name
from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView

from api.models import Expense


@login_required
def view_all_expenses(request):
    expenses = Expense.objects.filter(owner=request.user).order_by("date")
    context = {
        'expenses': expenses,
        'user': request.user.username
    }
    return render(request, 'frontend/expenses/all_expenses.html', context)


class ExpenseDetailView(LoginRequiredMixin, DetailView):
    model = Expense


class ExpenseCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Expense
    fields = ['name', 'amount', 'date', 'category', 'other_category', 'notes', 'account']
    success_message = 'Expense "%(name)s" Created'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


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
def view_year_expenses(request, year):
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=date(year, 1, 1),
                                      date__lte=date(year, 12, 31)).order_by("date")
    context = {
        'expenses': expenses,
        'user': request.user.username,
        'year': year
    }
    if len(expenses) > 0:
        return render(request, 'frontend/expenses/period_expenses.html', context)
    return render(request, 'frontend/expenses/no_expenses.html', context)


@login_required
def view_month_expenses(request, year, month):
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=date(year, int(month), 1),
                                      date__lte=date(year, int(month), 31)).order_by("date")
    context = {
        'expenses': expenses,
        'month': month_name[month],
        'year': year,
        'user': request.user.username
    }
    if len(expenses) > 0:
        return render(request, 'frontend/expenses/period_expenses.html', context)
    return render(request, 'frontend/expenses/no_expenses.html', context)