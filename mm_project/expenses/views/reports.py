import datetime

from django.db.models import Sum
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import FormView

from expenses.forms import MonthYearForm
from expenses.lookups import get_budgets_with_expense_totals, get_uncategorized_expenses_for_user, \
    get_monthly_total_expenses_for_user, get_expense_categories_for_user, get_budgets
from expenses.models import ExpenseCategory, Budget, Expense
from mm_project.log_utils import write_error_log, write_log

from services.calendar import handle_calendar_scroll, get_year_choices, get_month_choices


class MonthlyExpenseReportView(FormView):
    template_name = "reports/monthly.html"
    form_class = MonthYearForm

    def get_month_year_from_request(self):
        """Extract month and year from GET or POST parameters."""
        today = datetime.date.today()

        # Check GET parameters first (for URL query params)
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')

        # Fall back to POST parameters (for HTMX requests)
        if not month:
            month = self.request.POST.get('month')
        if not year:
            year = self.request.POST.get('year')

        # Convert to integers, defaulting to today's date
        try:
            month = int(month) if month else today.month
            year = int(year) if year else today.year
        except (ValueError, TypeError):
            month = today.month
            year = today.year

        return month, year

    def get_context_data(self, **kwargs):
        month = kwargs.pop('month', None)
        year = kwargs.pop('year', None)

        # If not provided in kwargs, get from request
        if month is None or year is None:
            month, year = self.get_month_year_from_request()

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
        non_budget_total = uncategorized_expenses.aggregate(total=Sum('amount'))['total'] or 0
        context['non_budget_total'] = non_budget_total

        context['budgets'] = get_budgets_with_expense_totals(
            user=self.request.user,
            month=month,
            year=year
        )

        today = datetime.date.today()
        context['month_choices'] = get_month_choices()
        context['year_choices'] = get_year_choices(today=today)

        context['selected_month'] = str(month)
        context['selected_year'] = str(year)

        context['show_summary'] = any([
            monthly_expense_total,
            non_budget_total,
        ])

        context['budget_choices'] = get_budgets(user=self.request.user)

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
                    write_error_log("Monthly Report", f"Cannot assign {category} to budget {budget}; {e}")
                else:
                    category.budget_category_id = budget
                    category.save()
            case "category":
                category_id = self.request.POST.get('category_update')
                expense_id = self.request.POST.get('expense_id')
                try:
                    category = ExpenseCategory.objects.get(id=category_id, owner=self.request.user)
                    expense = Expense.objects.get(id=expense_id, owner=self.request.user)
                except (
                        ExpenseCategory.DoesNotExist, ExpenseCategory.MultipleObjectsReturned,
                        Expense.DoesNotExist, Expense.MultipleObjectsReturned,
                ) as e:
                    write_error_log("Monthly Report", f"Cannot assign expense {expense_id} to category {category_id}; {e}")
                else:
                    expense.category = category
                    expense.save()

                    # If the new category has a budget, remove the row (return empty response)
                    if category.budget_category_id is not None:
                        return HttpResponse("")

                    # Otherwise, return the updated row with the new category name
                    context = {
                        'expense': expense,
                        'budget_choices': get_budgets(user=self.request.user)
                    }
                    return render(self.request, 'reports/components/uncategorized-expense-row.html', context)

        year = self.request.POST.get('year')
        month = self.request.POST.get('month')

        if action := self.request.POST.get("scroll"):
            month, year = handle_calendar_scroll(action, month, year)

        response = self.render_to_response(self.get_context_data(year=int(year), month=int(month)))

        # Add HX-Push-Url header to update the browser URL
        from django.urls import reverse
        new_url = f"{reverse('expenses:reports_monthly')}?month={month}&year={year}"
        response['HX-Push-Url'] = new_url

        return response


def get_expense_category_form(request, expense_id):
    try:
        expense_obj = Expense.objects.filter(owner=request.user).get(id=expense_id)
    except (Expense.DoesNotExist, Expense.MultipleObjectsReturned) as e:
        write_error_log("Report Expense Category Edit Inline", f"Cannot lookup expense object {expense_id}; {e}")
        return HttpResponseBadRequest()

    context = {
        "expense": expense_obj,
        "category_id": expense_obj.category_id,
        "expense_categories":  get_expense_categories_for_user(request.user)
    }

    return render(request, 'reports/components/category-edit-inline.html', context)


def get_expenses_for_budget(request, budget_id):

    month = request.POST.get("month")
    year = request.POST.get("year")

    all_expenses = Expense.objects.filter(owner=request.user, category__budget_category_id=budget_id, date__month=month, date__year=year).order_by('date')
    return render(
        request,
        "reports/components/budget-expenses-table.html",
        {
            "all_expenses": all_expenses,
        }

    )
