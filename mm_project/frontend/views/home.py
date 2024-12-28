import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.shortcuts import render

from accounts.models import Account
from bills.models import Bill
from expenses.models import Expense


@login_required
def frontend_home(request):
    latest_bills = Bill.objects.filter(owner=request.user).order_by('last_paid')[:3]
    largest_accounts = Account.objects.filter(owner=request.user).order_by('-balance')[:3]
    recent_expenses = Expense.objects.filter(owner=request.user).order_by('-date')[:5]

    accounts_data = (
        Account.objects.filter(owner=request.user)
        .aggregate(
            total=Sum('balance'),
            count=Count('id'),
        )
    )

    bills_data = (
        Bill.objects.filter(owner=request.user)
        .aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
    )

    expenses_data = (
        Expense.objects.filter(
            owner=request.user,
            date__month=datetime.datetime.now().month,
        )
        .aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
    )

    context = {
        # Cards Data
        'account_total': accounts_data['total'] or 0,
        'account_count': accounts_data['count'],
        'bill_total': bills_data['total'] or 0,
        'bill_count': bills_data['count'],
        'expense_total': expenses_data['total'] or 0,
        'expense_count': expenses_data['count'],

        # Summary Data
        'accounts': largest_accounts,
        'bills': latest_bills,
        'expenses': recent_expenses,
    }

    return render(request, "frontend/home.html", context)
