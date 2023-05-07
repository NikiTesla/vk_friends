from django.db import models
from django.contrib.auth.models import User

class FriendshipRequest(models.Model):
    from_user = models.ForeignKey(User, related_name="from_user", on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name="to_user", on_delete=models.CASCADE)
    created_at = models.DateTimeField("created", auto_now_add=True)
    status = models.CharField(choices=(('pending', 'Pending'),
                                       ('accepted', "Accepted"),
                                       ('rejected', 'Rejected'),
                                       ('withdrawed', 'Withdrawed')),
                                       default='pending', max_length=20)
    
    class Meta:
        db_table = 'friendship_requests' 

    def __str__(self) -> str:
        return f"Friendship request from {self.from_user} to {self.to_user} created at {self.created_at} has status {self.status}"
    