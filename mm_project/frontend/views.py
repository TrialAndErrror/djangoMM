from django.shortcuts import render, redirect, Http404
from api.models import User, Bill, Account
from api.forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView

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
def view_summary(request):
    bills = Bill.objects.filter(owner=request.user).order_by('next_due')[:3]
    accounts = Account.objects.filter(owner=request.user).order_by('-balance')[:3]
    context = {
        'bills': bills,
        'accounts': accounts,
        'user': request.user.username
    }

    return render(request, "frontend/overview.html", context)


@login_required
def view_all_bills(request):
    bills = Bill.objects.filter(owner=request.user)

    context = {
        'bills': bills,
        'user': request.user.username
    }

    return render(request, 'frontend/all_bills.html', context)


@login_required
def view_all_accounts(request):
    accounts = Account.objects.filter(owner=request.user)
    context = {
        'accounts': accounts,
        'user': request.user.username
    }
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


class BillDetailView(LoginRequiredMixin, DetailView):
    model = Bill


class AccountDetailView(LoginRequiredMixin,DetailView):
    model = Account


class AccountCreateView(LoginRequiredMixin, CreateView):
    model = Account
    fields = ['name', 'balance', 'type']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class BillUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Bill
    fields = ['name', 'amount', 'variable', 'last_paid', 'period', 'account']

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.owner:
            return True
        return False


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


class BillDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Bill
    success_url = '/bills/'

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
