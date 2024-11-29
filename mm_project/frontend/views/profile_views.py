from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.http import Http404
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
        Expense.objects.filter(owner=request.user)
        .aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
    )

    context = {
        # Cards Data
        'account_total': accounts_data['total'],
        'account_count': accounts_data['count'],
        'bill_total': bills_data['total'],
        'bill_count': bills_data['count'],
        'expense_total': expenses_data['total'],
        'expense_count': expenses_data['count'],

        # Summary Data
        'accounts': largest_accounts,
        'bills': latest_bills,
        'expenses': recent_expenses,
    }

    return render(request, "frontend/home.html", context)


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


def logout_view(request):
    logout(request)
    return render(request, "frontend/profile/loggedout.html", {})
