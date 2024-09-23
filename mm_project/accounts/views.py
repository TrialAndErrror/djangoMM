from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView

from accounts.models import Account


# Create your views here.
@login_required
def view_all_accounts(request):
    accounts = Account.objects.filter(owner=request.user).order_by("balance")
    context = {
        'accounts': accounts,
        'user': request.user.username
    }
    return render(request, 'accounts/all_accounts.html', context)


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
        return self.request.user == self.get_object().owner


class AccountDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Account
    success_url = '/accounts/'
    success_message = 'Account "%(name)s" Deleted'

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super().delete(request, *args, **kwargs)

    def test_func(self):
        return self.request.user == self.get_object().owner