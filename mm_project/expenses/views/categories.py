import datetime


from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, FormView
from rest_framework.reverse import reverse_lazy

from expenses.forms import MonthYearForm
from expenses.models import ExpenseCategory, Budget


class ExpenseCategoryDetailView(LoginRequiredMixin, DetailView):
    template_name = "expense_categories/view.html"
    model = ExpenseCategory


class ExpenseCategoryCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    template_name = "expense_categories/create.html"
    model = ExpenseCategory
    fields = ['name', 'description', 'owner']

    def get_success_message(self, cleaned_data):
        return f'Expense Category "{cleaned_data.get('name')}" Created'

    def get_form(self, *args, **kwargs):
        form = super(ExpenseCategoryCreateView, self).get_form(*args, **kwargs)
        form.fields['owner'].initial = self.request.user
        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ExpenseCategoryUpdateView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = "expense_categories/edit.html"
    model = ExpenseCategory
    fields = ['name', 'description']

    def get_success_message(self, cleaned_data):
        return f'Expense "{cleaned_data.get('name')}" Updated'

    def test_func(self):
        return self.request.user == self.get_object().owner


class ExpenseCategoryDeleteView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = "expense_categories/delete.html"
    model = ExpenseCategory
    success_url = reverse_lazy('expenses:expense_category_list')

    def get_success_message(self, cleaned_data):
        return f'Expense Category "{cleaned_data.get('name')}" Deleted'

    def test_func(self):
        return self.request.user == self.get_object().owner


class ViewExpenseCategoriesList(LoginRequiredMixin, FormView):
    template_name = "expense_categories/list.html"
    model = ExpenseCategory
    form_class = MonthYearForm

    def get_initial(self):
        """Prefill the form with the current month and year."""
        current_date = datetime.datetime.now()
        return {
            'month': current_date.month,
            'year': current_date.year,
        }

    def get(self, request, *args, **kwargs):
        """Handle GET requests to render the form."""
        expenses = ExpenseCategory.objects.filter(
            owner=self.request.user
        ).order_by("name").all()
        form = self.get_form()
        form.set_target_url(reverse_lazy('expenses:expense_category_list'))

        return render(request, self.template_name, {'form': form, 'expense_categories': expenses})


def htmx_list_update_budget(request, category_id):
    category = ExpenseCategory.objects.get(id=category_id)
    if request.method == 'POST':
        new_budget = request.POST.get('budget')
        if new_budget:
            category.budget_category_id = new_budget
        else:
            category.budget_category_id = None
        category.save()
        context = {'category': category}
        return render(request, 'expense_categories/components/editable-category-row.html', context)

    all_budgets = Budget.objects.filter(owner=request.user).order_by("name").all()

    context = {
        'choices': all_budgets,
        'selected_id': category.budget_category_id,
        'category': category,
    }

    return render(request, 'expense_categories/components/edit-category-row-inline.html', context)