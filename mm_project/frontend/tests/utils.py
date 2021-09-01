import datetime
import random
import string
from api.models import ACCOUNT_CHOICES, Account, User, PERIOD_CHOICES, Bill, EXPENSE_CHOICES, Expense


def get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join((random.choice(letters_and_digits) for i in range(length)))


def random_user_data():
    user_data = {
        "username": get_random_alphanumeric_string(20),
        "email": f'{get_random_alphanumeric_string(20)}@{get_random_alphanumeric_string(10)}.com',
        "password": get_random_alphanumeric_string(20),
    }
    return User.objects.create_user(
            username=user_data["username"],
            email=user_data['email'],
            password=user_data['password'],
        )


def random_account_data():
    account_data = {
        "name": get_random_alphanumeric_string(20),
        "balance": random.randint(0, 10000),
        "type": random.choice(ACCOUNT_CHOICES)[0]
    }
    return Account(
        name=account_data["name"],
        balance=account_data["balance"],
        type=account_data["type"]
    )


def random_bill_data():
    bill_data = {
        "name": get_random_alphanumeric_string(20),
        "amount": random.randint(0, 10000),
        "variable": random.choice([True, False]),
        "day": random.randint(0, 31),
        "period": random.choice(PERIOD_CHOICES)[0]
    }
    # TODO: Test without day
    return Bill(
        name=bill_data["name"],
        amount=bill_data["amount"],
        variable=bill_data["variable"],
        day=bill_data["day"],
        period=bill_data["period"]
    )


def random_expense_data():
    expense_data = {
        "name": get_random_alphanumeric_string(20),
        "amount": random.randint(0, 10000),
        "date": get_random_date(),
        "category": random.choice(EXPENSE_CHOICES)[0],
        "notes": get_random_alphanumeric_string(20)
    }
    expense_obj = Expense(
        name=expense_data["name"],
        amount=expense_data["amount"],
        date=expense_data["date"],
        category=expense_data["category"],
        notes=expense_data["notes"]
    )
    if expense_data["category"] == "Other":
        expense_obj.other_category = get_random_alphanumeric_string(20)
    return expense_obj


def get_random_date():
    start_date = datetime.date(2020, 1, 1)
    end_date = datetime.date(2020, 2, 1)

    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    return random_date
