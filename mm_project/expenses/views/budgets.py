from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.shortcuts import render
from django.views.generic import FormView

from expenses.forms import MonthYearForm
from expenses.lookups import get_annotated_budget_categories, get_uncategorized_expenses
from expenses.models import CategoryBudget


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
        form = self.get_form()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        """Handle POST requests to process the form."""
        form_class = self.get_form_class()
        form = form_class(data=request.POST)
        context = {'form': form, 'budgets': [], 'uncategorized_expenses': []}
        if form.is_valid():
            context['budgets'] = get_annotated_budget_categories(
                target_year=form.cleaned_data['year'],
                target_month=form.cleaned_data['month'],
            )
            context['uncategorized_expenses'] = get_uncategorized_expenses(
                target_year=form.cleaned_data['year'],
                target_month=form.cleaned_data['month'],
            )
            return render(request, self.template_name, context)

        return render(request, self.template_name, context, status=400)
