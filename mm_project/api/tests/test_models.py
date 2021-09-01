from django.test import TestCase
from api.models import Account, Bill, Expense

from .utils import random_account_data, random_user_data, random_bill_data, random_expense_data


class TestCreateAccount(TestCase):
    def setUp(self) -> None:
        self.user = random_user_data()
        self.user.save()

        self.account = random_account_data()
        self.account.owner = self.user
        self.account.save()

        self.recorded_account = Account.objects.get(name=self.account.name)

    def test_account_created(self):
        self.assertEqual(len(Account.objects.all()), 1)

    def test_name_correct(self):
        self.assertEqual(self.recorded_account.name, self.account.name)

    def test_balance_correct(self):
        self.assertEqual(self.recorded_account.balance, self.account.balance)

    def test_type_correct(self):
        self.assertTrue(self.recorded_account.type, self.account.type)

    def test_owner_correct(self):
        self.assertTrue(self.recorded_account.owner, self.user)


class TestCreateBill(TestCase):
    def setUp(self) -> None:
        self.user = random_user_data()
        self.user.save()

        self.account = random_account_data()
        self.account.owner = self.user
        self.account.save()

        self.bill = random_bill_data()
        self.bill.owner = self.user
        self.bill.account = self.account
        self.bill.save()

        self.recorded_bill = Bill.objects.get(name=self.bill.name)

    def test_account_created(self):
        self.assertEqual(len(Bill.objects.all()), 1)

    def test_name_correct(self):
        self.assertEqual(self.recorded_bill.name, self.bill.name)

    def test_amount_correct(self):
        self.assertEqual(self.recorded_bill.amount, self.bill.amount)

    def test_variable_correct(self):
        self.assertEqual(self.recorded_bill.variable, self.bill.variable)

    def test_day_correct(self):
        self.assertEqual(self.recorded_bill.day, self.bill.day)

    def test_period_correct(self):
        self.assertEqual(self.recorded_bill.period, self.bill.period)

    def test_owner_correct(self):
        self.assertEqual(self.recorded_bill.owner, self.user)


class TestCreateExpense(TestCase):
    def setUp(self) -> None:
        self.user = random_user_data()
        self.user.save()

        self.account = random_account_data()
        self.account.owner = self.user
        self.account.save()

        self.expense = random_expense_data()
        self.expense.owner = self.user
        self.expense.account = self.account
        self.expense.save()

        self.recorded_expense = Expense.objects.get(name=self.expense.name)

    def test_account_created(self):
        self.assertEqual(len(Expense.objects.all()), 1)

    def test_name_correct(self):
        self.assertEqual(self.recorded_expense.name, self.expense.name)

    def test_amount_correct(self):
        self.assertEqual(self.recorded_expense.amount, self.expense.amount)

    def test_category_correct(self):
        self.assertEqual(self.recorded_expense.category, self.expense.category)
        # if self.expense.category == 'Other':
        self.assertEqual(self.recorded_expense.other_category, self.expense.other_category)

    def test_date_correct(self):
        self.assertEqual(self.recorded_expense.date, self.expense.date)

    def test_notes_correct(self):
        self.assertEqual(self.recorded_expense.notes, self.expense.notes)

    def test_owner_correct(self):
        self.assertEqual(self.recorded_expense.owner, self.user)

    def test_account_correct(self):
        self.assertEqual(self.recorded_expense.account, self.account)


