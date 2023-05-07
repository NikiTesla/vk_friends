from django.test import TestCase, RequestFactory
from .models import UserProfile
from django.contrib.auth.models import User, AnonymousUser

class TestUsers(TestCase):
    # function to test views to return 200 code when GET
    def codeTest(self, adress: str, code: int):
        response = self.client.get(adress)
        self.assertEqual(response.status_code, code)

    def test_index(self):
        self.codeTest("/", 200)

    def test_user_login(self):
        self.codeTest("/login", 200)

    def test_user_signup(self):
        self.codeTest("/signup", 200)