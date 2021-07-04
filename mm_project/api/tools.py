import datetime
import os
from django.db.models import Count

from dateutil.relativedelta import relativedelta
from matplotlib import pyplot as plt

from io import BytesIO
import base64

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


def make_chart(labels, sizes):
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
    ax1.axis('equal')
    # ax1.plot(labels, sizes)
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    plt.rcParams.update({'font.size': 14})
    plt.tight_layout()


def make_homepage_context_dict(accounts, bills, expenses, username):
    accounts_balances = [item.balance for item in accounts]
    expense_balances = [item.amount for item in expenses]

    accounts_total = sum(accounts_balances)
    expenses_total = sum(expense_balances)
    bill_total = sum([entry.amount * BILLS_CONVERTER[entry.period] for entry in bills])

    context = {
        'account_total': accounts_total,
        'account_count': accounts.aggregate(Count('id'))['id__count'],
        'bill_total': bill_total,
        'bill_count': bills.aggregate(Count('id'))['id__count'],
        'expense_total': expenses_total,
        'expense_count': expenses.aggregate(Count('id'))['id__count'],
        'user': username
    }

    context.update(make_graphs(accounts, bills, expenses))

    return context


"""
Matplotlib integration with Django
https://www.youtube.com/watch?v=jrT6NiM46jk
"""


def new_get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=60)
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph


def new_get_plot(labels, sizes):
    plt.switch_backend('AGG')
    make_chart(labels, sizes)
    graph = new_get_graph()
    return graph


def make_graphs(accounts, bills, expenses):
    accounts_balances = [item.balance for item in accounts]
    accounts_balances_for_charts = [item if item > 0 else 0 for item in accounts_balances]
    accounts_labels = [item.name for item in accounts]

    bills_labels = [item.name for item in bills]
    bills_balances = [item.amount for item in bills]

    expense_categories = set([item.category for item in expenses])
    expense_amounts = [sum([item.amount if item.category == category else 0 for item in expenses])
                       for category in expense_categories]

    return {
        'graph_b': new_get_plot(bills_labels, bills_balances),
        'graph_a': new_get_plot(accounts_labels, accounts_balances_for_charts),
        'graph_e': new_get_plot(expense_categories, expense_amounts)
    }
