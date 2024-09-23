from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView, DeleteView, CreateView

from accounts.models import Account
from api.forms import BillPayForm, BillCreateForm, BillUpdateForm
from api.tools import get_next_date

from bills.models import Bill


# Create your views here.
@login_required
def view_all_bills(request):
    bills = Bill.objects.filter(owner=request.user).order_by("last_paid")

    context = {
        'bills': bills,
        'user': request.user.username
    }

    return render(request, 'bills/all_bills.html', context)


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
                bill.account.balance -= amount_paid
                bill.save()
                bill.account.save()
                messages.success(request, f'Bill {bill.name} paid from {bill.account.name}.')
                return redirect(reverse_lazy('bills:bill_detail', kwargs={"pk": bill.id}))

    form = BillPayForm({
        "amount": bill.amount,
        "date_paid": bill.next_due
    })
    context = {
        'form': form,
        'object': bill,
        'user': request.user.username
    }
    return render(request, "bills/pay_bill.html", context)


class BillDetailView(LoginRequiredMixin, DetailView):
    model = Bill


class BillCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Bill
    success_message = 'Bill %(name)s created successfully'
    form_class = BillCreateForm
    template_name = 'bills/bill_form.html'

    def get_form(self, **kwargs):
        form = super().get_form(form_class=kwargs.get('form_class'))
        form.fields['account'].queryset = Account.objects.filter(owner=self.request.user)
        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(BillCreateView, self).form_valid(form)


class BillUpdateView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Bill
    form_class = BillUpdateForm
    success_message = f'Bill %(name)s updated successfully'
    template_name = 'bills/bill_form.html'

    def test_func(self):
        return self.request.user == self.object.owner


class BillDeleteView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Bill
    success_url = reverse_lazy('bills:bill_list')
    success_message = 'Bill "%(name)s" Deleted'

    def test_func(self):
        return self.request.user == self.object.owner
