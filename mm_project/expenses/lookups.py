import datetime

from django.contrib.auth.models import User
from django.db.models import Subquery, OuterRef, Sum, Q
from django.db.models.functions import Coalesce
from django.db.models import DecimalField

from bills.models import Bill
from expenses.models import Budget, Expense, ExpenseCategory
from mm_project.log_utils import write_log


def get_budgets_with_expense_totals(user: User, month: int, year: int):
    return Budget.objects.filter(owner=user).annotate(
        total_spent=Coalesce(
            Subquery(
                Expense.objects.filter(
                    category__budget_category=OuterRef('pk'),
                    date__year=year,
                    date__month=month,
                ).values('category__budget_category')
                .annotate(total=Sum('amount'))
                .values('total')[:1],  # Subquery needs to return a single value
                output_field=DecimalField()
            ),
            0,  # If no related expenses, default to 0
            output_field=DecimalField()
        )
    )


def get_monthly_total_expenses_for_user(user: User, month: int, year: int):
    query =  Expense.objects.filter(
        date__year=year,
        date__month=month,
        owner=user,
        amount__gt=0,
    ).aggregate(total=Sum('amount'))['total']
    write_log("Monthly total expenses:", query)
    return query


def get_uncategorized_expenses_for_user(user: User, month: int, year: int):
    return (
        Expense.objects.filter(
            Q(category__budget_category__isnull=True),
            date__year=year,
            date__month=month,
            owner=user,
            amount__gt=0,
        )
        .order_by("category__name")
        .all()
    )


def get_unpaid_bills_for_user(user: User):
    all_bills = Bill.objects.filter(owner=user).all()

    today = datetime.date.today()
    return sum([
        bill.amount
        for bill in all_bills
        if (
                bill.next_due.month == today.month
                and bill.next_due.day > today.day
        )
    ])


def get_expense_categories_for_user(user: User):
    return ExpenseCategory.objects.filter(owner=user).order_by('name')
