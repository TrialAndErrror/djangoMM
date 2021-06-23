from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import Http404
from django.shortcuts import render

from api.models import Bill, Account, Expense
from api.tools import make_graphs, BILLS_CONVERTER


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


def logout_view(request):
    logout(request)
    return render(request, "frontend/profile/loggedout.html", {})