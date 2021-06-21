from django.shortcuts import render, redirect, Http404
from api.models import User, Bill, Account
from api.forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView

from api.tools import get_next_date


# Create your views here.
def frontend_home(request):
    return render(request, "frontend/home.html", {})


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
            'user': request.user.first_name
        }
        return render(request, "frontend/profile.html", context)


@login_required
def view_all_bills(request):
    bills = Bill.objects.filter(owner=request.user)
    # for bill in bills:
    #     if not bill.next_due:
    #         next_date = get_next_date(bill.last_paid, bill.period)
    #         bill.next_due = next_date
    #         bill.save()

    context = {
        'bills': bills,
        'user': request.user.username
    }
    print(context)

    return render(request, 'frontend/all_bills.html', context)


@login_required
def view_all_accounts(request):
    accounts = Account.objects.filter(owner=request.user)
    context = {
        'accounts': accounts,
        'user': request.user.username
    }
    print(context)
    return render(request, 'frontend/all_accounts.html', context)


def logout_view(request):
    logout(request)
    return render(request, "frontend/loggedout.html", {})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('frontend:home')
    else:
        form = UserRegisterForm()
    return render(request, 'frontend/register.html', {'form': form})


def add_bill(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('frontend:home')


class BillCreateView(LoginRequiredMixin, CreateView):
    model = Bill
    fields = ['name', 'amount', 'variable', 'last_paid', 'period', 'account']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.next_due = get_next_date(form.instance.last_paid, form.instance.period)
        return super().form_valid(form)


class BillDetailView(DetailView):
    model = Bill


class AccountCreateView(LoginRequiredMixin, CreateView):
    model = Account
    fields = ['name', 'balance', 'type']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
