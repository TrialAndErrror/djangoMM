from django.shortcuts import render, Http404, redirect
from api.models import User, Bill, Account, Expense

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.views.generic import CreateView, DetailView, UpdateView, DeleteView

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from django.db.models import Count

from api.tools import get_next_date, BILLS_CONVERTER, make_graphs

from datetime import date
from calendar import month_name


# Create your views here.
def frontend_home(request):
    bills = Bill.objects.filter(owner=request.user)
    accounts = Account.objects.filter(owner=request.user)
    expenses = Expense.objects.filter(owner=request.user)

    accounts_balances, expense_balances = make_graphs(accounts, bills, expenses, request.user.username)

    accounts_total = sum(accounts_balances)
    expenses_total = sum(expense_balances)

    bill_total = sum([entry.amount * BILLS_CONVERTER[entry.period] for entry in bills])

    context_dict = {
        'account_total': accounts_total,
        'account_count': accounts.aggregate(Count('id'))['id__count'],
        'bill_total': bill_total,
        'bill_count': bills.aggregate(Count('id'))['id__count'],
        'expense_total': expenses_total,
        'expense_count': expenses.aggregate(Count('id'))['id__count'],
        'user': request.user.username
    }
    return render(request, "frontend/home.html", context_dict)


@login_required
def view_profile(request):
    try:
        user_obj = User.objects.filter(id=request.user.id).first()
    except User.DoesNotExist:
        return Http404()
    else:
        print(user_obj.first_name)
        context = {
            'user_obj': user_obj,
            'user': request.user.username
        }
        return render(request, "frontend/profile/profile.html", context)


@login_required
def view_summary(request):
    bills = Bill.objects.filter(owner=request.user).order_by('next_due')[:3]
    accounts = Account.objects.filter(owner=request.user).order_by('-balance')[:3]
    expenses = Expense.objects.filter(owner=request.user).order_by('date')[:5]
    context = {
        'bills': bills,
        'accounts': accounts,
        'expenses': expenses,
        'user': request.user.username
    }

    return render(request, "frontend/summary/overview.html", context)


# def register(request):
#     if request.method == 'POST':
#         form = UserRegisterForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             messages.success(request, f'Account created for {username}!')
#             return redirect('frontend:home')
#     else:
#         form = UserRegisterForm()
#     return render(request, 'frontend/register.html', {'form': form})


# def add_bill(request):
#     if request.method == "POST":
#         form = UserRegisterForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             messages.success(request, f'Account created for {username}!')
#             return redirect('frontend:home')


@login_required
def view_all_bills(request):
    bills = Bill.objects.filter(owner=request.user).order_by("next_due")

    context = {
        'bills': bills,
        'user': request.user.username
    }

    return render(request, 'frontend/bills/all_bills.html', context)


@login_required
def pay_bill(request, pk):
    bill = Bill.objects.get(owner=request.user, id=pk)
    if bill:
        bill.last_paid = bill.next_due
        bill.next_due = get_next_date(bill.last_paid, bill.period)
        bill.save()
        messages.success(request, f'Bill {bill.name} marked as paid.')
        return redirect(f'/bills/{bill.id}/')


class BillDetailView(LoginRequiredMixin, DetailView):
    model = Bill


class BillCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Bill
    fields = ['name', 'amount', 'variable', 'last_paid', 'period', 'account']
    success_message = 'Bill "%(name)s" Created'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.next_due = get_next_date(form.instance.last_paid, form.instance.period)
        return super().form_valid(form)
    
    
class BillUpdateView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Bill
    fields = ['name', 'amount', 'variable', 'last_paid', 'period', 'account']
    success_message = 'Bill "%(name)s" Updated'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.next_due = get_next_date(form.instance.last_paid, form.instance.period)
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.owner:
            return True
        return False
    
        
class BillDeleteView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Bill
    success_url = '/bills/'
    success_message = 'Bill "%(name)s" Deleted'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.owner:
            return True
        return False


@login_required
def view_all_accounts(request):
    accounts = Account.objects.filter(owner=request.user).order_by("balance")
    context = {
        'accounts': accounts,
        'user': request.user.username
    }
    return render(request, 'frontend/accounts/all_accounts.html', context)


def logout_view(request):
    logout(request)
    return render(request, "frontend/profile/loggedout.html", {})


class AccountDetailView(LoginRequiredMixin, DetailView):
    model = Account


class AccountCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Account
    fields = ['name', 'balance', 'type']
    success_message = 'Account "%(name)s" Created'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class AccountUpdateView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Account
    fields = ['name', 'balance', 'type']
    success_message = 'Account "%(name)s" Updated'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.owner:
            return True
        return False


class AccountDeleteView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Account
    success_url = '/accounts/'
    success_message = 'Account "%(name)s" Deleted'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.owner:
            return True
        return False


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
