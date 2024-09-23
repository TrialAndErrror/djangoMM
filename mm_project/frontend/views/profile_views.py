from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render, redirect

from accounts.models import Account
from api.tools import make_homepage_context_dict
from bills.models import Bill
from expenses.models import Expense


@login_required
def frontend_home(request):
    bills = Bill.objects.filter(owner=request.user)
    accounts = Account.objects.filter(owner=request.user)
    expenses = Expense.objects.filter(owner=request.user)

    context = make_homepage_context_dict(accounts, bills, expenses, request.user.username)

    return render(request, "frontend/home.html", context)


@login_required
def refresh_graphs(request):
    bills = Bill.objects.filter(owner=request.user)
    accounts = Account.objects.filter(owner=request.user)
    expenses = Expense.objects.filter(owner=request.user)

    # TODO: Make the graph part

    return redirect('frontend:home')


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
    bills = Bill.objects.filter(owner=request.user).order_by('last_paid')[:3]
    accounts = Account.objects.filter(owner=request.user).order_by('-balance')[:3]
    expenses = Expense.objects.filter(owner=request.user).order_by('-date')[:5]
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