from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect, resolve_url
from django.views.generic import DetailView, DeleteView

from api.models import Bill
from api.tools import get_next_date
from api.forms import BillPayForm, BillCreateForm, BillUpdateForm


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

    if request.method == 'POST':
        form = BillPayForm(request.POST)
        if form.is_valid():
            amount_paid = form.cleaned_data.get("amount")
            date_paid = form.cleaned_data.get("date_paid")

            if amount_paid > bill.account.balance:
                messages.warning(request, f'Error: Not enough money in {bill.account.name} to pay bill. (Current Balance: {bill.account.balance})')
            else:
                bill.last_paid = date_paid
                bill.next_due = get_next_date(bill.last_paid, bill.period)
                bill.account.balance -= amount_paid
                bill.save()
                bill.account.save()
                messages.success(request, f'Bill {bill.name} paid from {bill.account.name}.')
                return redirect(f'/bills/{bill.id}/')

    form = BillPayForm({
        "amount": bill.amount,
        "date_paid": bill.next_due
    })
    context = {
        'form': form,
        'object': bill,
        'user': request.user.username
    }
    return render(request, "frontend/bills/pay_bill.html", context)


class BillDetailView(LoginRequiredMixin, DetailView):
    model = Bill


@login_required
def bill_create(request):
    if request.method == 'POST':
        form = BillCreateForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, form.success_message)
            # TODO: Could use error handling here

            return redirect(resolve_url("frontend:bill_detail", pk=form.cleaned_data.get("pk")))

    form = BillCreateForm(user=request.user)
    context = {
        'form': form,
        'user': request.user.username
    }
    return render(request, "api/bill_form.html", context)


@login_required
def bill_update_view(request, pk):
    selected_bill = Bill.objects.get(id=pk)

    if request.method == "POST":
        form = BillUpdateForm(request.POST, instance=selected_bill, user=request.user)
        if form.is_valid():
            form.save()

    form = BillUpdateForm(instance=selected_bill, user=request.user)
    return render(request, "api/bill_form.html", {"form": form})


class BillDeleteView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Bill
    success_url = '/bills/'
    success_message = 'Bill "%(name)s" Deleted'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.owner:
            return True
        return False
