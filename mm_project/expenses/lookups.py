from django.db.models import Q, Subquery, Sum

from expenses.models import Expense, CategoryBudget


def get_annotated_budget_categories(target_year: int, target_month: int):
    return CategoryBudget.objects.annotate(
        total_expenses=Sum(
            'category__expense__amount',
            filter=Q(category__expense__date__year=target_year) &
                   Q(category__expense__date__month=target_month)
        )
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
