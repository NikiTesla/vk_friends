from django.test import TestCase
from django.contrib.auth.models import User
from users.models import UserProfile
from django.urls import reverse


class TestFriendship(TestCase):
    # function to test views to return 200 code when GET
    def codeTest(self, adress: str, code: int):
        response = self.client.get(adress)
        self.assertEqual(response.status_code, code)

    def protectedTest(self, adress):
        user = User.objects.create(username='testtest', email='test@test.test', password='200test200')
        UserProfile.objects.create(user=user)

        self.codeTest(adress, 302)
        self.client.force_login(user)
        self.codeTest(adress, 200)

    def test_index(self):
        self.protectedTest(reverse("friendship_index"))
    
    def test_show_friends(self):
        self.protectedTest(reverse("show_friends"))

    def test_add_friend(self):
        self.protectedTest(reverse("add_friend"))
        
    
    def test_show_requests(self):
        self.protectedTest(reverse("show_requests"))
