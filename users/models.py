from django.db import models
from django.contrib.auth.models import User
from friendship.models import FriendshipRequest

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    friends = models.ManyToManyField(User, related_name="friends")
    requests = models.ManyToManyField(FriendshipRequest, related_name="friendship_requests")
    
    class Meta:
        db_table = 'users'

    def __str__(self) -> str:
        return self.user.username
    
