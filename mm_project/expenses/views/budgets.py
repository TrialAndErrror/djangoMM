from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import DetailView, CreateView, UpdateView, ListView
from rest_framework.reverse import reverse_lazy

from expenses.models import ExpenseCategory, Expense, Budget


class BudgetListView(LoginRequiredMixin, ListView):
    template_name = "budgets/budget-status.html"
    model = Budget
    context_object_name = "budgets"


class BudgetDetailView(LoginRequiredMixin, DetailView):
    model = Budget
    template_name = 'budgets/budget_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_choices'] = ExpenseCategory.objects.filter(budget_category_id__isnull=True, owner=self.request.user).order_by('name').values_list('id', 'name')
        if category := kwargs.get('category_id'):
            context['category'] = category
            expenses = Expense.objects.filter(category_id=category).order_by("date")

            # Group expenses by month
            expenses_by_month = {}
            for expense in expenses:
                month_key = expense.date.strftime('%Y-%m')
                month_display = expense.date.strftime('%B %Y')
                if month_key not in expenses_by_month:
                    expenses_by_month[month_key] = {
                        'month_display': month_display,
                        'expenses': []
                    }
                expenses_by_month[month_key]['expenses'].append(expense)

            # Sort by month (most recent first)
            context['expenses_by_month'] = dict(sorted(expenses_by_month.items(), reverse=True))
        return context

    def post(self, request, *args, **kwargs):
        category_id = request.POST.get('category_id')
        category = ExpenseCategory.objects.get(id=category_id, owner=self.request.user)

        if self.request.POST.get("action") == "remove":
            category.budget_category_id = None
        else:
            category.budget_category_id = self.get_object().id

        category.save()
        return self.get(request, *args, **kwargs)


class BudgetCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Budget
    fields = ['name', 'amount', 'owner']
    template_name = 'budgets/budget_create.html'

    def get_success_url(self):
        return reverse_lazy('expenses:budget_view', kwargs={'pk': self.object.pk})

    def get_success_message(self, cleaned_data):
        return f'Budget Category "{cleaned_data.get('name')}" Created'

    def get_form(self, *args, **kwargs):
        form = super(BudgetCreateView, self).get_form(*args, **kwargs)
        form.fields['owner'].initial = self.request.user
        form.fields['owner'].widget.attrs.update({
            'hidden': True,
        })
        form.fields['owner'].label = ''
        return form


class BudgetUpdateView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Budget
    fields = ['name', 'amount']
    template_name = 'budgets/budget_edit.html'

    def get_success_url(self):
        return reverse_lazy('expenses:budget_view', kwargs={'pk': self.object.pk})




    def get_success_message(self, cleaned_data):
        return f'Budget "{cleaned_data.get('name')}" Updated'

    def test_func(self):
        return self.request.user == self.get_object().owner