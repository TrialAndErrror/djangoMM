from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse


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
        self.assertEqual(url, '/')

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
