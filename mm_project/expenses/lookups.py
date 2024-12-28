from decimal import Decimal

from django.db.models import Q, Subquery, Sum, OuterRef, DecimalField, Value, When, Case, F, CharField
from django.db.models.functions import Coalesce, Cast

from expenses.models import Expense, CategoryBudget, ExpenseCategory


def get_annotated_budget_categories(target_year: int, target_month: int):
    budget_amt_subquery = CategoryBudget.objects.filter(
        category=OuterRef('id')
    ).values('amount')[:1]

    budget_id_subquery = CategoryBudget.objects.filter(
        category=OuterRef('id')
    ).values('id')[:1]

    return ExpenseCategory.objects.annotate(
        total_expenses=Coalesce(
            Sum(
                'expense__amount',
                filter=Q(expense__date__year=target_year) &
                       Q(expense__date__month=target_month)
            ),
            0,
            output_field=DecimalField()
        ),
        budget_amt=Coalesce(Subquery(budget_amt_subquery), Decimal(0)),
        budget_id=Subquery(budget_id_subquery),

    )


def get_uncategorized_expenses(target_year: int, target_month: int):
    budgeted_categories = CategoryBudget.objects.values('category')

    # Get all uncategorized expenses filtered by the target month and year
    uncategorized_expenses = Expense.objects.filter(
        Q(category__isnull=True) | ~Q(category__in=Subquery(budgeted_categories)),
        date__year=target_year,
        date__month=target_month
    ).aggregate(total=Sum('amount'))['total']
    return uncategorized_expenses
