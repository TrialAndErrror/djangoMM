from django.test import TestCase
from django.urls import reverse


class LoggedOutTestCase(TestCase):
    def check_for_redirect(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/login/?next={url}')


class TestLoggedOutHome(LoggedOutTestCase):
    def test_get_home(self):
        url = reverse("frontend:home")
        self.check_for_redirect(url)

    def test_get_profile(self):
        url = reverse("frontend:profile")
        self.check_for_redirect(url)

    def test_get_summary(self):
        url = reverse("frontend:summary")
        self.check_for_redirect(url)

    def test_get_refresh_graphs(self):
        url = reverse("frontend:refresh")
        self.check_for_redirect(url)


class TestLoggedOutBills(LoggedOutTestCase):
    def test_get_bills_home(self):
        url = reverse("frontend:all_bills")
        self.check_for_redirect(url)

    def test_view_one_bill(self):
        bill_id = 1
        url = reverse("frontend:bill_detail", args=[bill_id])
        self.check_for_redirect(url)

    def test_update_one_bill(self):
        bill_id = 1
        url = reverse("frontend:bill_update", args=[bill_id])
        self.check_for_redirect(url)

    def test_delete_one_bill(self):
        bill_id = 1
        url = reverse("frontend:bill_delete", args=[bill_id])
        self.check_for_redirect(url)
        
class TestLoggedOutAccounts(LoggedOutTestCase):
    def test_get_accounts_home(self):
        url = reverse("frontend:all_accounts")
        self.check_for_redirect(url)

    def test_view_one_account(self):
        account_id = 1
        url = reverse("frontend:account_detail", args=[account_id])
        self.check_for_redirect(url)

    def test_update_one_account(self):
        account_id = 1
        url = reverse("frontend:account_update", args=[account_id])
        self.check_for_redirect(url)

    def test_delete_one_account(self):
        account_id = 1
        url = reverse("frontend:account_delete", args=[account_id])
        self.check_for_redirect(url)


class TestLoggedOutExpenses(LoggedOutTestCase):
    def test_get_expenses_home(self):
        url = reverse("frontend:all_expenses")
        self.check_for_redirect(url)

    def test_view_one_expense(self):
        expense_id = 1
        url = reverse("frontend:expense_detail", args=[expense_id])
        self.check_for_redirect(url)

    def test_update_one_expense(self):
        expense_id = 1
        url = reverse("frontend:expense_update", args=[expense_id])
        self.check_for_redirect(url)

    def test_delete_one_expense(self):
        expense_id = 1
        url = reverse("frontend:expense_delete", args=[expense_id])
        self.check_for_redirect(url)
