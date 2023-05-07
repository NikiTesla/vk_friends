from .models import FriendshipRequest
from django.contrib.auth.models import User
from rest_framework import serializers
from users.models import UserProfile


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


def get_requests_serialized(user: UserProfile):
    """function to serialize incoming and outcoming requests for user"""
    try:
        incoming = user.requests.filter(to_user=user.user, status="pending")
        ser_incoming = IncomeFriendshipRequestsSerializer(incoming, many=True).data
    except FriendshipRequest.DoesNotExist:
        ser_incoming = []

    try:
        outcoming = user.requests.filter(from_user=user.user, status="pending")
        ser_outcoming = OutcomeFriendshipRequestsSerializer(outcoming, many=True).data
    except FriendshipRequest.DoesNotExist:
        ser_outcoming = []

    return (ser_incoming, ser_outcoming)