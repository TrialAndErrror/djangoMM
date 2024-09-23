import datetime
import os
from django.db.models import Count

from dateutil.relativedelta import relativedelta

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


def get_next_date(date, days_in_period):
    return date + datetime.timedelta(days=days_in_period)


def make_chart(labels, sizes):
    # TODO: reimplement charts

    raise NotImplemented()
    # fig1, ax1 = plt.subplots()
    # """
    # Sort labels and remove labels for smaller sections.
    #
    # Third parameter is the decimal representation of the percentage that acts as the cutoff;
    # i.e. 0.05 means "Remove any labels of sections that are 5% of the total or smaller"
    # """
    # labels, sizes = sort_labels(labels, sizes, .05)
    #
    # """
    # Make pie chart.
    # Only shows labels that are above the threshold indicated in sort_labels.
    # """
    # # ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
    # ax1.pie(sizes, labels=labels, shadow=True, startangle=90)
    #
    # ax1.axis('equal')
    #
    # """
    # Setup center white circle.
    # """
    # centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    # fig = plt.gcf()
    # fig.gca().add_artist(centre_circle)
    #
    # """
    # Set font size.
    # """
    # plt.rcParams.update({'font.size': 14})

    # plt.legend(labels=labels, bbox_to_anchor=(0.5, -0.25))


def sort_labels(labels, sizes, threshold=0):
    """
    Combine labels and sizes for sorting, then return as two lists.

    Threshold is a float that represents the smallest percentage section that should have its label displayed.
    i.e. threshold=0.2 means "Do not display the label of a section if the amount is less than 20%
    of the overall total bills.

    :param labels: list
    :param sizes: list
    :param threshold: float
    :return: list, list
    """

    """
    Disable short list to show all labels (i.e. ignore threshold).
    If you set an optional threshold, short_list is set to false.
    """
    short_list = True if threshold != 0 else False

    """
    Combine labels and sizes into a list of tuples
    """
    data_list = [(labels[i], sizes[i]) for i in range(len(labels))]

    """
    Sort data_list based on index 1 of the inner tuples.
    Create account sum to determine which labels should be cut off.
    """
    data_list.sort(key=lambda x: x[1])
    accounts_sum = sum(sizes)

    labels = []
    sizes = []

    """
    Loop through data_list and deconstruct the labels and sizes into separate lists
    """
    for i in range(len(data_list)):
        """
        If a section is below the size threshold, set its label as an empty string.
        """
        if short_list and data_list[i][1]/accounts_sum < threshold:
            labels.append('')
        else:
            labels.append(data_list[i][0])

        sizes.append(data_list[i][1])
    return labels, sizes


def make_homepage_context_dict(accounts, bills, expenses, username):
    """
    Make context dict for the homepage.

    Comprised of accounts info, bills info, and expenses info, as well as the username of the logged-in user.

    :param accounts: list
    :param bills: list
    :param expenses: list
    :param username: str
    :return: dict
    """

    accounts_balances = [item.balance for item in accounts]
    expense_balances = [item.amount for item in expenses]

    """
    Get the sum of the accounts and expenses.
    
    For bills, we divide by 30 to get an approximate monthly total
    """
    accounts_total = sum(accounts_balances)
    expenses_total = sum(expense_balances)
    bill_total = sum([float(entry.amount) * (float(entry.period) / 30) for entry in bills])

    """
    This is the data that will go into the homepage
    """
    context = {
        'account_total': round(accounts_total, 2),
        'account_count': accounts.aggregate(Count('id'))['id__count'],
        'bill_total': round(bill_total, 2),
        'bill_count': bills.aggregate(Count('id'))['id__count'],
        'expense_total': round(expenses_total, 2),
        'expense_count': expenses.aggregate(Count('id'))['id__count'],
        'user': username
    }

    """
    Adding the graphs directly to the context dictionary to be passed into the template directly.
    """
    # TODO: Add charts
    # context.update(make_graphs(accounts, bills, expenses))

    return context


def new_get_graph():
    """
    Matplotlib integration with Django
    https://www.youtube.com/watch?v=jrT6NiM46jk
    """
    raise NotImplemented

    # buffer = BytesIO()
    # plt.savefig(buffer, format='png', dpi=60)
    # buffer.seek(0)
    # image_png = buffer.getvalue()
    # graph = base64.b64encode(image_png)
    # graph = graph.decode('utf-8')
    # buffer.close()
    # return graph


def new_get_plot(labels, sizes):
    """
    Matplotlib integration with Django
    https://www.youtube.com/watch?v=jrT6NiM46jk
    """
    raise NotImplemented

    # plt.switch_backend('AGG')
    # make_chart(labels, sizes)
    graph = new_get_graph()
    return graph


def make_graphs(accounts, bills, expenses):
    """
    Make graphs from data and return the graph images as a dictionary.

    :param accounts: list
    :param bills: list
    :param expenses: list
    :return: dict
    """

    """
    Process account balances.
    
    Only includes balances with a positive balance; might need to rework for credit accounts.
    Currently, graph doesn't support negative balances.
    """
    accounts_balances = [item.balance for item in accounts]
    accounts_balances_for_charts = [item if item > 0 else 0 for item in accounts_balances]
    accounts_labels = [item.name for item in accounts]

    """
    Process bills labels and balances. 
    
    Bills have already been adjusted for their period in make_homepage_context_dict above.
    """
    bills_labels = [item.name for item in bills]
    bills_balances = [item.amount for item in bills]

    """
    Process expense labels and balances.
    
    Expenses are shown on graph based on their category, so they need to be 
    """
    expense_categories = list(set([item.category for item in expenses]))
    expense_amounts = [sum([item.amount if item.category == category else 0 for item in expenses])
                       for category in expense_categories]

    return {}
    return {
        'graph_b': new_get_plot(bills_labels, bills_balances),
        'graph_a': new_get_plot(accounts_labels, accounts_balances_for_charts),
        'graph_e': new_get_plot(expense_categories, expense_amounts)
    }
