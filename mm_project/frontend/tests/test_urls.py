from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from api.models import Bill, Expense, Account
from .utils import random_bill_data, random_user_data, random_account_data


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
        one_bill = Bill.objects.get(name=self.bill.name)
        # self.assertEqual(one_bill, self.bill)

        url = reverse("frontend:bill_update", args=[one_bill.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'api/bill_form.html')

        self.new_bill = random_bill_data()

        # TODO: Why does this test fail?
        self.client.post(url, data={
            "name": self.new_bill.name
        })

        updated_bill = Bill.objects.first()
        self.assertEqual(updated_bill, self.new_bill)

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

