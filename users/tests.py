from django.test import TestCase
from .models import UserProfile, User
from django.urls import reverse

class TestUsers(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testtest2", password="200test200")
        self.user.save()
        self.user_profile = UserProfile.objects.create(user=self.user)
        self.user_profile.save()
    
    def codeTest(self, adress: str, code: int):
        """
        function to test views on returning 200 code when GET"""
        response = self.client.get(adress)
        self.assertEqual(response.status_code, code)
    
    def dataTest(self, adress: str, data: dict):
        for k, v in zip(data["sent"], data["expected"]):
            response = self.client.post(adress, data=k, content_type="application/json")
            self.assertEqual(response.content.decode("utf-8"), v)

    def test_index(self):
        self.codeTest(reverse("index"), 200)

    def test_user_signup(self):
        self.codeTest(reverse("user_signup"), 200)
        data = {
            "sent": [
                {
                    "username":"testtest2",
                    "password1":"200test200",
                    "password2": "200test200",
                    "email": "test@test.com"
                },
                {
                    "username":"testtest",
                    "password1":"200test",
                    "password2": "200test200",
                    "email": "test@test.com"
                },
                {
                    "username":"testtest",
                    "password1":"200test200",
                    "password2": "200test200",
                    "email": "testtest.com"
                },
                {
                    "username":"test",
                    "password1":"200test200",
                    "password2": "200test200",
                    "email": "testtest.com"
                },
                {
                    "username":"testtest3",
                    "password1":"200test200",
                    "password2": "200test200",
                    "email": "test@test.com"
                },
            ],
            "expected": [
                r'"Username already exists"',
                r'"Passwords are different"',
                r'"Email is incorrect"',
                r'"Username should contain 6 or more symbols. Password should contain 8 or more symbols"',
                r'"You was signed up and logged in"'
            ]
        }

        self.dataTest(reverse("user_signup"), data)

    def test_user_login(self):
        self.codeTest(reverse("user_login"), 200)
        data = {
            "sent": [
                {
                    "username": "testtest2",
                    "password": "200test200"
                },
                {
                    "username": "testest",
                    "password": "200test200"
                },
                {
                    "username": "testtest",
                    "password": "200test2"
                },
                {
                    "password":""
                }
            ],
            "expected": [
                r'"Logged in successfully"',
                r'"Invalid login or password"',
                r'"Invalid login or password"',
                r'"You should propose both username and password fields"'
            ]
        }

        self.dataTest(reverse("user_login"), data)

    def test_user_logout(self):
        user = User.objects.create(username="testtest", password="200test200")
        self.client.force_login(user=user)

        response = self.client.get(reverse("user_logout"))
        self.assertEqual(response.content.decode("utf-8"), r'"You were logged out"')

