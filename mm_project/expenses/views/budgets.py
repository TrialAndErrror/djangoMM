from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render, redirect
from django.views.generic import FormView, DetailView, CreateView, UpdateView
from rest_framework.reverse import reverse_lazy

from expenses.forms import MonthYearForm
from expenses.lookups import get_annotated_budget_categories, get_uncategorized_expenses
from expenses.models import CategoryBudget, ExpenseCategory, Expense


class ViewBudgetStatus(LoginRequiredMixin, FormView):
    template_name = "budgets/budget-status.html"
    model = CategoryBudget
    form_class = MonthYearForm

    def get_initial(self):
        """Prefill the form with the current month and year."""
        current_date = datetime.now()
        return {
            'month': current_date.month,
            'year': current_date.year,
        }

    def get(self, request, *args, **kwargs):
        """Handle GET requests to render the form."""
        initial_data = self.get_initial()
        categories = get_annotated_budget_categories(
            target_year=initial_data['year'],
            target_month=initial_data['month'],
        )
        form = self.get_form()
        form.set_target_url(reverse_lazy('expenses:budget_list'))
        return render(request, self.template_name, {'form': form, 'categories': categories})

    def post(self, request, *args, **kwargs):
        """Handle POST requests to process the form."""
        form_class = self.get_form_class()
        form = form_class(data=request.POST)
        form.set_target_url(reverse_lazy('expenses:budget_list'))
        context = {'form': form, 'budgets': []}
        if form.is_valid():
            context['categories'] = get_annotated_budget_categories(
                target_year=form.cleaned_data['year'],
                target_month=form.cleaned_data['month'],
            )

            return render(request, self.template_name, context)

        return render(request, self.template_name, context, status=400)


class BudgetDetailView(LoginRequiredMixin, DetailView):
    model = CategoryBudget
    template_name = 'budgets/budget_view.html'


class BudgetCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = CategoryBudget
    fields = ['category', 'amount', 'owner']
    template_name = 'budgets/budget_create.html'

    def get_success_url(self):
        return reverse_lazy('expenses:budget_view', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_choices'] = ExpenseCategory.objects.values_list('id', 'name')
        context['matching_expenses'] = Expense.objects.filter(category=self.kwargs.get('category_id'))
        return context

    def get_success_message(self, cleaned_data):
        return f'Budget Category "{cleaned_data.get('category')}" Created'

    def get_form(self, *args, **kwargs):
        form = super(BudgetCreateView, self).get_form(*args, **kwargs)
        form.fields['category'].queryset = ExpenseCategory.objects.filter(expense__owner=self.request.user).distinct()
        selected_category = self.kwargs.get('category_id')
        if selected_category:
            form.fields['category'].initial = selected_category

        form.fields['owner'].initial = self.request.user
        form.fields['owner'].widget.attrs.update({
            'hidden': True,
        })
        form.fields['owner'].label = ''

        return form


class BudgetUpdateView(SuccessMessageMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CategoryBudget
    fields = ['amount']
    template_name = 'budgets/budget_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_choices'] = ExpenseCategory.objects.values_list('id', 'name')
        context['matching_expenses'] = Expense.objects.filter(category=self.object.category)
        return context

    def get_success_message(self, cleaned_data):
        return f'Budget "{cleaned_data.get('name')}" Updated'

    def test_func(self):
        return self.request.user == self.get_object().owner


class BudgetMergeView(FormView):
    def post(self, request, *args, **kwargs):
        data = request.POST
        selected_category_id = data.get('selected-category')
        expenses_list = Expense.objects.filter(category_id=selected_category_id).all()

        new_category_id = data.get('target-category')
        for expense in expenses_list:
            expense.category_id = new_category_id
            expense.save()

        budget_obj = CategoryBudget.objects.get(category_id=selected_category_id)
        if budget_obj:
            budget_obj.delete()

        return redirect(reverse_lazy('expenses:budget_list'))





