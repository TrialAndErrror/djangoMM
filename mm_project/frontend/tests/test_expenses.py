from django.contrib.auth.models import User
from django.forms import model_to_dict
from django.test import TestCase, Client
from django.urls import reverse

from api.models import Account, Expense
from frontend.tests.utils import random_account_data, random_expense_data


class TestExpensesUrls(TestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestCase, cls).setUpClass()
        test_user = User.objects.create_user(
            username="test_user",
            email="test@trialanderrror.com",
            password="test_password"
        )

        test_user.save()

        account = random_account_data()
        account.owner = test_user
        account.save()

    def setUp(self):
        self.owner = User.objects.first()
        self.account = Account.objects.first()

        self.expense = random_expense_data()
        self.expense.owner = self.owner
        self.expense.account = self.account
        self.expense.save()

        self.client = Client()
        self.client.login(username="test_user", password="test_password")

    def test_get_expenses_home(self):
        url = reverse("frontend:all_expenses")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/expenses/show_expenses.html')

    def test_view_one_expense(self):
        one_expense = Expense.objects.first()
        self.assertEqual(one_expense, self.expense)

        url = reverse("frontend:expense_detail", args=[one_expense.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'api/expense_detail.html')

    def test_update_one_expense(self):
        one_expense = Expense.objects.get(pk=self.expense.pk)

        url = reverse("frontend:expense_update", args=[one_expense.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'api/expense_form.html')

        self.new_expense = random_expense_data()

        new_data = {key: value if value else '' for key, value in model_to_dict(one_expense).items()}
        new_data["name"] = self.new_expense.name
        self.client.post(url, data=new_data)

        updated_expense = Expense.objects.get(name=self.new_expense.name)
        self.assertEqual(updated_expense, one_expense)

        url = reverse("frontend:expense_update", args=[updated_expense.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'api/expense_form.html')

    def test_change_expense_account(self):
        one_expense = Expense.objects.get(pk=self.expense.pk)
        url = reverse("frontend:expense_update", args=[one_expense.pk])

        new_account = random_account_data()
        new_account.owner = self.owner
        new_account.save()

        account_2 = Account.objects.get(name=new_account.name)

        old_balance_1 = self.account.balance
        old_balance_2 = new_account.balance

        # TODO: Fix this test
        new_data = {key: value if value else '' for key, value in model_to_dict(one_expense).items()}
        new_data["account"] = account_2.pk
        self.client.post(url, data=new_data)

        updated_expense = Expense.objects.get(pk=self.expense.pk)
        # self.assertEqual(updated_expense.account, new_account)

        expense_amount = one_expense.amount

        new_balance_1 = Account.objects.get(name=self.account.name).balance
        new_balance_2 = Account.objects.get(name=account_2.name).balance

        self.assertEqual(old_balance_1 + updated_expense.amount, new_balance_1)
        self.assertEqual(old_balance_2 - expense_amount, new_balance_2)

    def test_delete_one_expense(self):
        one_expense = Expense.objects.first()
        self.assertEqual(one_expense, self.expense)

        url = reverse("frontend:expense_delete", args=[one_expense.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'api/expense_confirm_delete.html')

        url = reverse("frontend:expense_delete", args=[one_expense.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 302)
