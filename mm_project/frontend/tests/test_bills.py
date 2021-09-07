from django.contrib.auth.models import User
from django.forms import model_to_dict
from django.test import TestCase, Client
from django.urls import reverse

from api.models import Account, Bill
from frontend.tests.utils import random_account_data, random_bill_data


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

        self.new_bill = random_bill_data()
        data_dict = model_to_dict(one_bill)
        new_data = {key: value if value else '' for key, value in data_dict.items()}
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