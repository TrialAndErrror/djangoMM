from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.forms.models import model_to_dict

from api.models import Bill, Expense, Account
from .utils import random_bill_data, random_user_data, random_account_data, random_expense_data


class TestUrlPaths(TestCase):
    def test_home_path(self):
        url = reverse("frontend:home")
        self.assertEqual(url, '/')


class TestHomeUrls(TestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestCase, cls).setUpClass()
        test_user = User.objects.create_user(
            username="test_user",
            email="test@trialanderrror.com",
            password="test_password"
        )

        test_user.save()

    def setUp(self):
        self.client = Client()
        self.client.login(username="test_user", password="test_password")

    def test_get_home(self):
        url = reverse("frontend:home")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'frontend/home.html')

    def test_get_profile(self):
        url = reverse("frontend:profile")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'frontend/profile/profile.html')

    def test_get_summary(self):
        url = reverse("frontend:summary")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'frontend/summary/overview.html')

    def test_get_refresh_graphs(self):
        url = reverse("frontend:refresh")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


class TestBillsUrls(TestCase):
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

        self.bill = random_bill_data()
        self.bill.owner = self.owner
        self.bill.account = self.account
        self.bill.save()

        self.client = Client()
        self.client.login(username="test_user", password="test_password")

    def test_get_bills_home(self):
        url = reverse("frontend:all_bills")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/bills/all_bills.html')

    def test_view_one_bill(self):
        one_bill = Bill.objects.first()
        self.assertEqual(one_bill, self.bill)

        url = reverse("frontend:bill_detail", args=[one_bill.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'api/bill_detail.html')

    def test_update_one_bill(self):
        one_bill = Bill.objects.get(id=self.bill.id)

        url = reverse("frontend:bill_update", args=[one_bill.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'api/bill_form.html')

        # TODO: Figure out why this passes all the data into the id field
        self.new_bill = random_bill_data()
        new_data = {key: value if value else '' for key, value in model_to_dict(one_bill).items()}
        new_data["name"] = self.new_bill.name
        new_data["account"] = self.account.pk
        self.client.post(url, data=new_data)

        updated_bill = Bill.objects.get(name=self.new_bill.name)
        one_bill = Bill.objects.get(id=self.bill.id)
        self.assertEqual(updated_bill, one_bill)

        url = reverse("frontend:bill_update", args=[updated_bill.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'api/bill_form.html')

    def test_delete_one_bill(self):
        one_bill = Bill.objects.first()
        self.assertEqual(one_bill, self.bill)

        url = reverse("frontend:bill_delete", args=[one_bill.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'api/bill_confirm_delete.html')

        url = reverse("frontend:bill_delete", args=[one_bill.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 302)


class TestAccountsUrls(TestCase):
    @classmethod
    def setUpTestData(cls):
        super(TestCase, cls).setUpClass()
        test_user = User.objects.create_user(
            username="test_user",
            email="test@trialanderrror.com",
            password="test_password"
        )

        test_user.save()

    def setUp(self):
        self.owner = User.objects.first()
        self.account = random_account_data()
        self.account.owner = self.owner
        self.account.save()

        self.client = Client()
        self.client.login(username="test_user", password="test_password")

    def test_get_accounts_home(self):
        url = reverse("frontend:all_accounts")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/accounts/all_accounts.html')

    def test_view_one_account(self):
        one_account = Account.objects.first()
        self.assertEqual(one_account, self.account)

        url = reverse("frontend:account_detail", args=[one_account.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'api/account_detail.html')

    def test_update_one_account(self):
        one_account = Account.objects.get(pk=self.account.pk)

        url = reverse("frontend:account_update", args=[one_account.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'api/account_form.html')

        self.new_account = random_bill_data()

        new_data = {key: value if value else '' for key, value in model_to_dict(one_account).items()}
        new_data["name"] = self.new_account.name

        self.client.post(url, data=new_data)

        test_account = Account.objects.get(name=self.new_account.name)
        self.assertEqual(test_account, one_account)

        url = reverse("frontend:account_update", args=[test_account.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'api/account_form.html')

    def test_delete_one_account(self):
        one_account = Account.objects.first()
        self.assertEqual(one_account, self.account)

        url = reverse("frontend:account_delete", args=[one_account.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'api/account_confirm_delete.html')

        url = reverse("frontend:account_delete", args=[one_account.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 302)


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