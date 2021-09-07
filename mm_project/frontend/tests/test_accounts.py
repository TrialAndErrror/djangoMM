from django.contrib.auth.models import User
from django.forms import model_to_dict
from django.test import TestCase, Client
from django.urls import reverse

from api.models import Account
from frontend.tests.utils import random_account_data, random_bill_data


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