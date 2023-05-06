from .models import FriendshipRequest
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)

class IncomeFriendshipRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendshipRequest
        fields = ('from_user', 'created_at', 'status')

class OutcomeFriendshipRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendshipRequest
        fields = ('to_user', 'created_at', 'status')