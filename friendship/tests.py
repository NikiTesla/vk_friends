from django.test import TestCase
from users.models import UserProfile, User
from django.urls import reverse
from .models import FriendshipRequest


class TestFriendship(TestCase):
    def codeTest(self, adress: str, code: int):
        """
        Function to test views to return 200 code when GET"""
        response = self.client.get(adress)
        self.assertEqual(response.status_code, code)

    def setUp(self):
        self.user = User.objects.create_user(username='test_user', email='user@test.test', password='200test200')
        self.user.save()
        self.user_profile = UserProfile.objects.create(user=self.user)
        self.user_profile.save()
        self.client.force_login(user=self.user)

    def test_index(self):
        self.codeTest(reverse("friendship_index"), 200)

    def test_show_friends(self):
        self.codeTest(reverse("show_friends"), 200)

        friend = User.objects.create_user(username="friend1", password="friend1", email="friend1@fr.com")
        friend.save()
        UserProfile.objects.create(user=friend).save()

        self.user_profile.friends.add(friend)

        response = self.client.get(reverse("show_friends"))
        self.assertEqual(response.content.decode("utf-8"), r'{"friends":[{"username":"friend1"}]}')


    def test_add_friend(self):
        self.codeTest(reverse("add_friend"), 200)
        friend = User.objects.create_user(username="friend1", password="friend1", email="friend1@fr.com")
        friend.save()
        UserProfile.objects.create(user=friend).save()

        response = self.client.post(reverse("add_friend"), data={"username":"friend1"}, content_type="application/json")
        self.assertEqual(response.content.decode("utf-8"), r'"Request was sent"')

        
    
    def test_show_requests(self):
        self.codeTest(reverse("show_requests"), 200)

        friend = User.objects.create_user(username="friend1", password="friend1", email="friend1@fr.com")
        friend.save()
        UserProfile.objects.create(user=friend).save()

        request = FriendshipRequest.objects.create(from_user=self.user, to_user=friend)
        self.user_profile.requests.add(request)

        response = self.client.get(reverse("show_requests"))
        self.assertEqual(response.content.decode("utf-8"), r'{"user":"test_user","outcoming":[{"to_user":%d,"created_at":"%s","status":"pending"}],"incoming":[]}' %
                        (request.to_user.id, request.created_at.isoformat()[:-6]+"Z"))