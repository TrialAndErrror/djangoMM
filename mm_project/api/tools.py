import datetime
import os
from django.db.models import Count

from dateutil.relativedelta import relativedelta
from matplotlib import pyplot as plt


a_month = relativedelta(months=1)
calc_date = {
    'Daily': datetime.timedelta(days=1),
    'Weekly': datetime.timedelta(weeks=1),
    'Bi-Weekly': datetime.timedelta(weeks=2),
    'Monthly': a_month,
    'Quarterly': a_month * 3,
    'Semi-Annual': a_month * 6,
    'Annual': a_month * 12
}

BILLS_CONVERTER = {
    "Daily": 30,
    "Weekly": 4,
    "Bi-Weekly": 2,
    "Monthly": 1,
    "Quarterly": 1 / 3,
    "Semi-Annual": 1 / 6,
    "Annual": 1 / 12,
}


def get_next_date(date, period):
    return date + calc_date[period]


def make_pie_chart(labels, sizes, user, name):
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
    ax1.axis('equal')
    plt.rcParams.update({'font.size': 10, 'figure.figsize': (3.0, 3.0)})
    plt.tight_layout()
    plt.savefig(f'{os.getcwd()}/media/{user}/piechart_{name}.png')


def make_context_dict(accounts, bills, expenses, username):
    accounts_balances = [item.balance for item in accounts]
    expense_balances = [item.amount for item in expenses]

    accounts_total = sum(accounts_balances)
    expenses_total = sum(expense_balances)
    bill_total = sum([entry.amount * BILLS_CONVERTER[entry.period] for entry in bills])

    return {
        'account_total': accounts_total,
        'account_count': accounts.aggregate(Count('id'))['id__count'],
        'bill_total': bill_total,
        'bill_count': bills.aggregate(Count('id'))['id__count'],
        'expense_total': expenses_total,
        'expense_count': expenses.aggregate(Count('id'))['id__count'],
        'user': username
    }


def make_graphs(accounts, bills, expenses, username):
    accounts_balances = [item.balance for item in accounts]
    accounts_balances_for_charts = [item if item > 0 else 0 for item in accounts_balances]
    accounts_labels = [item.name for item in accounts]

    bills_labels = [item.name for item in bills]
    bills_balances = [item.amount for item in bills]

    expense_categories = set([item.category for item in expenses])
    expense_amounts = [sum([item.amount if item.category == category else 0 for item in expenses])
                       for category in expense_categories]

    os.makedirs(f'{os.getcwd()}/media/{username}/', exist_ok=True)
    for fig_name in ['accounts', 'bills', 'expenses']:
        path = f'{os.getcwd()}/media/{username}/piechart_{fig_name}.png'
        if os.path.exists(path):
            os.remove(path)

    make_pie_chart(bills_labels, bills_balances, username, 'bills')
    make_pie_chart(accounts_labels, accounts_balances_for_charts, username, 'accounts')
    make_pie_chart(expense_categories, expense_amounts, username, 'expenses')