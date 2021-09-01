from django.test import SimpleTestCase
from django.urls import reverse, resolve


class TestUrls(SimpleTestCase):
    def test_home(self):
        url = reverse('frontend.home')
        print(resolve(url))
