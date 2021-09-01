from django.test import TestCase, Client
from django.urls import reverse
from .utils import get_random_alphanumeric_string
from django.contrib.auth.models import User
from django.contrib.auth import get_user


class TestRegisterUrls(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('register')

    def test_register_url(self):
        print(f'Checking string representation of {self.url}')
        self.assertEqual(self.url, '/register/')

    def test_get_register(self):
        print(f'Sending get request to {self.url}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_register(self):
        password = get_random_alphanumeric_string(20)
        form_data = {
            "username": get_random_alphanumeric_string(20),
            "first_name": get_random_alphanumeric_string(10),
            "last_name": get_random_alphanumeric_string(15),
            "email": f'{get_random_alphanumeric_string(20)}@{get_random_alphanumeric_string(10)}.com',
            "password1": password,
            "password2": password
        }
        print(f'Using form data: {form_data}')
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 302)


class TestLoginUrls(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('login')

        self.user_data = {
            "username": get_random_alphanumeric_string(20),
            "email": f'{get_random_alphanumeric_string(20)}@{get_random_alphanumeric_string(10)}.com',
            "password": get_random_alphanumeric_string(20),
        }
        self.user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
        )
        self.user.save()

        self.login_data = self.user_data.copy()
        self.login_data.pop("email")

    def test_register_url(self):
        print(f'Checking string representation of {self.url}')
        self.assertEqual(self.url, '/login/')

    def test_get_register(self):
        print(f'Sending get request to {self.url}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_login(self):
        print(f'Original user data: {self.user_data}')
        print(f'Using login data: {self.login_data}')
        response = self.client.post(self.url, self.login_data)
        self.assertEqual(response.status_code, 302)

        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user, self.user)


class TestLogoutUrls(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('logout')

        self.user_data = {
            "username": get_random_alphanumeric_string(20),
            "email": f'{get_random_alphanumeric_string(20)}@{get_random_alphanumeric_string(10)}.com',
            "password": get_random_alphanumeric_string(20),
        }
        self.user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
        )
        self.user.save()

        self.login_data = self.user_data.copy()
        self.login_data.pop("email")

        self.client.post(self.url, self.login_data)

    def test_logout_url(self):
        print(f'Checking string representation of {self.url}')
        self.assertEqual(self.url, '/logout/')

    def test_get_logout(self):
        print(f'Sending get request to {self.url}')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
