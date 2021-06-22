from django.shortcuts import render, Http404
from api.models import User, Bill, Account, Expense

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView

from django.db.models import Count

from api.tools import get_next_date

from datetime import date
from calendar import month_name


# Create your views here.
def frontend_home(request):
    bills = Bill.objects.filter(owner=request.user)
    accounts = Account.objects.filter(owner=request.user)
    expenses = Expense.objects.filter(owner=request.user)

    converter = {
        "day": 30,
        "week": 4,
        "biweek": 2,
        "month": 1,
        "quarter": 1/3,
        "biyear": 1/6,
        "year": 1/12,
    }

    accounts_total = sum(
        [entry.balance
         for entry in accounts]
    )
    bill_total = sum(
        [entry.amount * converter[entry.period]
         for entry in bills]
    )
    expenses_total = sum(
        [entry.amount
         for entry in expenses]
    )

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
    bills = Bill.objects.filter(owner=request.user)

    context = {
        'bills': bills,
        'user': request.user.username
    }

    return render(request, 'frontend/bills/all_bills.html', context)


class BillDetailView(LoginRequiredMixin, DetailView):
    model = Bill


class BillCreateView(LoginRequiredMixin, CreateView):
    model = Bill
    fields = ['name', 'amount', 'variable', 'last_paid', 'period', 'account']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.next_due = get_next_date(form.instance.last_paid, form.instance.period)
        return super().form_valid(form)
    
    
class BillUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Bill
    fields = ['name', 'amount', 'variable', 'last_paid', 'period', 'account']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.next_due = get_next_date(form.instance.last_paid, form.instance.period)
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.owner:
            return True
        return False
    
        
class BillDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Bill
    success_url = '/bills/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.owner:
            return True
        return False


@login_required
def view_all_accounts(request):
    accounts = Account.objects.filter(owner=request.user)
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


class AccountCreateView(LoginRequiredMixin, CreateView):
    model = Account
    fields = ['name', 'balance', 'type']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class AccountUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Account
    fields = ['name', 'balance', 'type']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.owner:
            return True
        return False


class AccountDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Account
    success_url = '/accounts/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.owner:
            return True
        return False


@login_required
def view_all_expenses(request):
    expenses = Expense.objects.filter(owner=request.user)
    context = {
        'expenses': expenses,
        'user': request.user.username
    }
    return render(request, 'frontend/expenses/all_expenses.html', context)


class ExpenseDetailView(LoginRequiredMixin, DetailView):
    model = Expense


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    fields = ['name', 'amount', 'date', 'category', 'other_category', 'notes', 'account']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ExpenseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Expense
    fields = ['name', 'amount', 'date', 'category', 'other_category', 'notes', 'account']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.owner:
            return True
        return False


class ExpenseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Expense
    success_url = '/accounts/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.owner:
            return True
        return False


@login_required
def view_year_expenses(request, year):
    expenses = Expense.objects.filter(owner=request.user,
                                      date__gte=date(year, 1, 1),
                                      date__lte=date(year, 12, 31))
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
                                      date__lte=date(year, int(month), 31))
    context = {
        'expenses': expenses,
        'month': month_name[month],
        'year': year,
        'user': request.user.username
    }
    if len(expenses) > 0:
        return render(request, 'frontend/expenses/period_expenses.html', context)
    return render(request, 'frontend/expenses/no_expenses.html', context)
