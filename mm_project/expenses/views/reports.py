import datetime

from django.db.models import Sum
from django.views.generic import FormView

from expenses.forms import MonthYearForm
from expenses.lookups import get_budgets_with_expense_totals, get_uncategorized_expenses_for_user, \
    get_monthly_total_expenses_for_user, get_expense_categories_for_user
from expenses.models import ExpenseCategory, Budget, Expense
from mm_project.log_utils import write_error_log, write_log


class MonthlyExpenseReportView(FormView):
    template_name = "reports/monthly.html"
    form_class = MonthYearForm

    def get_context_data(self, **kwargs):
        today = datetime.date.today()
        month = kwargs.pop('month', today.month)
        year = kwargs.pop('year', today.year)

        context = super().get_context_data(**kwargs)

        monthly_expense_total = get_monthly_total_expenses_for_user(
            user=self.request.user,
            month=month,
            year=year
        )
        context['monthly_total'] = monthly_expense_total

        uncategorized_expenses = get_uncategorized_expenses_for_user(
            user=self.request.user,
            month=month,
            year=year,
        )

        context['uncategorized_expenses'] = uncategorized_expenses
        non_budget_total = uncategorized_expenses.aggregate(total=Sum('amount'))['total']
        context['non_budget_total'] = non_budget_total

        context['budgets'] = get_budgets_with_expense_totals(
            user=self.request.user,
            month=month,
            year=year
        )

        context['expense_categories'] = get_expense_categories_for_user(self.request.user)

        # Month Choices
        context['month_choices'] = [(str(i), datetime.datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)]
        context['selected_month'] = str(month)
        # Year Choices (current year +/- 10 years)
        context['year_choices'] = [(str(year), year) for year in range(today.year - 10, today.year + 11)]
        context['selected_year'] = str(year)

        context['show_summary'] = any([
            monthly_expense_total,
            non_budget_total,
        ])

        return context

    def post(self, *args, **kwargs):
        form_type = self.request.POST.get('form_type')


        match form_type:
            case "budget":
                category = self.request.POST.get('category')
                budget_id = self.request.POST.get('budget')
                try:
                    category = ExpenseCategory.objects.get(id=category, owner=self.request.user)
                    budget = Budget.objects.get(id=budget_id, owner=self.request.user)
                except (
                        ExpenseCategory.DoesNotExist, ExpenseCategory.MultipleObjectsReturned,
                        Budget.DoesNotExist, Budget.MultipleObjectsReturned,
                ) as e:
                    write_error_log("Monthly Report", f"Cannot assign {category_name} to budget {budget}; {e}")
                else:
                    category.budget_category_id = budget
                    category.save()
            case "category":
                category = self.request.POST.get('category_update')
                expense_id = self.request.POST.get('expense_id')
                try:
                    category = ExpenseCategory.objects.get(id=category, owner=self.request.user)
                    expense = Expense.objects.get(id=expense_id)
                except (
                        ExpenseCategory.DoesNotExist, ExpenseCategory.MultipleObjectsReturned,
                        Expense.DoesNotExist, Expense.MultipleObjectsReturned,
                ) as e:
                    write_error_log("Monthly Report", f"Cannot assign expense {expense_id} to category {category}; {e}")
                else:
                    expense.category_id = category
                    expense.save()

        year = self.request.POST.get('year')
        month = self.request.POST.get('month')
        return self.render_to_response(self.get_context_data(year=year, month=month))
