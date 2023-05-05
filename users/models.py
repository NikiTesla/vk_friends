from django.db import models

class User(models.Model):
    username = models.CharField("Name", max_length=100, unique=True)
    password = models.CharField("Password", max_length=255)
    email = models.CharField("Email", max_length=200)
    
    class Meta:
        db_table = 'users'

    def __str__(self) -> str:
        return "User " + self.name
    

class FriendshipRequest(models.Model):
    datetime = models.DateTimeField("Datetime", auto_now=True)
    user_from = models.IntegerField("user id from who")
    user_to = models.IntegerField("user id to whom")

    class Meta:
        db_table = 'requests'