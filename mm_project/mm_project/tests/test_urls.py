from django.test import TestCase, Client
from django.urls import reverse, resolve


class TestUrls(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_url(self):
        url = reverse('register')
        self.assertEqual(url, '/register/')

    def test_get_home(self):
        url = reverse('register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
