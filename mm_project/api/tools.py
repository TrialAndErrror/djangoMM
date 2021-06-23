import datetime
import os

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
    plt.savefig(f'media/{user}/piechart_{name}.png')


def make_graphs(accounts, bills, expenses, username):
    accounts_balances = [item.balance for item in accounts]
    bills_balances = [item.amount for item in bills]
    expense_balances = [item.amount for item in expenses]
    accounts_labels = [item.name for item in accounts]
    bills_labels = [item.name for item in bills]
    expenses_labels = [item.name for item in expenses]

    os.makedirs(f'{os.getcwd()}/media/{username}/', exist_ok=True)
    for fig_name in ['accounts', 'bills', 'expenses']:
        os.remove(f'{os.getcwd()}/media/{username}/piechart_{fig_name}.png')

    make_pie_chart(bills_labels, bills_balances, username, 'bills')
    make_pie_chart(accounts_labels, accounts_balances, username, 'accounts')
    make_pie_chart(expenses_labels, expense_balances, username, 'expenses')

    return accounts_balances, expense_balances