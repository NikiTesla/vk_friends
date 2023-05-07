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

        self.friend = User.objects.create_user(username="friend1", password="friend1", email="friend1@fr.com")
        self.friend.save()
        self.friend_profile = UserProfile.objects.create(user=self.friend)
        self.friend_profile.save()

    def test_index(self):
        self.codeTest(reverse("friendship_index"), 200)

    def test_show_friends(self):
        self.codeTest(reverse("show_friends"), 200)
        self.user_profile.friends.add(self.friend)

        response = self.client.get(reverse("show_friends"))
        self.assertEqual(response.content.decode("utf-8"), r'{"friends":[{"username":"friend1"}]}')


    def test_add_friend(self):
        self.codeTest(reverse("add_friend"), 200)

        response = self.client.post(reverse("add_friend"), data={"username":"friend1"}, content_type="application/json")
        self.assertEqual(response.content.decode("utf-8"), r'"Request was sent"')
    
    def test_show_requests(self):
        self.codeTest(reverse("show_requests"), 200)

        request = FriendshipRequest.objects.create(from_user=self.user, to_user=self.friend)
        self.user_profile.requests.add(request)

        response = self.client.get(reverse("show_requests"))
        self.assertEqual(response.content.decode("utf-8"), r'{"user":"test_user","outcoming":[{"to_user":%d,"created_at":"%s","status":"pending"}],"incoming":[]}' %
                        (request.to_user.id, request.created_at.isoformat()[:-6]+"Z"))
        
    def test_accept(self):
        request = FriendshipRequest.objects.create(from_user=self.user, to_user=self.friend)
        self.user_profile.requests.add(request)
        self.friend_profile.requests.add(request)

        response = self.client.put(reverse("accept"), data={"from_user":self.friend.id}, content_type="application/json")
        self.assertEqual(response.content.decode("utf-8"), r'"now you are friends"')

    def test_withdraw(self):
        request = FriendshipRequest.objects.create(from_user=self.user, to_user=self.friend)
        self.user_profile.requests.add(request)
        self.friend_profile.requests.add(request)

        response = self.client.put(reverse("withdraw"), data={"to_user":self.user.id}, content_type="application/json")
        self.assertEqual(response.content.decode("utf-8"), r'"request was withdrawed"')

    def test_reject(self):
        request = FriendshipRequest.objects.create(from_user=self.user, to_user=self.friend)
        self.user_profile.requests.add(request)
        self.friend_profile.requests.add(request)

        response = self.client.put(reverse("reject"), data={"from_user":self.friend.id}, content_type="application/json")
        self.assertEqual(response.content.decode("utf-8"), r'"request was rejected"')

    def test_delete_friend(self):
        request = FriendshipRequest.objects.create(from_user=self.user, to_user=self.friend, status="accepted")
        self.user_profile.requests.add(request)
        self.friend_profile.requests.add(request)
        self.user_profile.friends.add(self.friend)

        response = self.client.delete(reverse("delete_friend"), {"from_user":self.friend.username}, content_type="application/json")
        self.assertEqual(response.content.decode("utf-8"), r'"friend %s was deleted"'%self.friend.username)

    def test_send_message(self):
        response = self.client.post(reverse("send_message"), data={"to_user":self.friend.id}, content_type="application/json")
        self.assertEqual(response.content.decode("utf-8"), r'{"message":"Hello!","to_user":%d}'%self.friend.id)