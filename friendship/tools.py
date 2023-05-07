from users.models import UserProfile, User
from .models import FriendshipRequest
from django.contrib import auth

def accept_request(from_user: UserProfile, to_user: UserProfile):
    """
    Internal function gets user is sending request, user is accepting request, makes them friends"""
    from_user.friends.add(to_user.user)
    to_user.friends.add(from_user.user)

    change_status_of_request(from_user, to_user, "accepted")


def get_user_friend_profiles(request, friend_id):
    """
    internal function that returns user_profile and friend_profile with id friend_id"""
    user_profile = UserProfile.objects.get(user=auth.get_user(request))

    friend = User.objects.get(id=friend_id)
    friend_profile = UserProfile.objects.get(user=friend)

    return user_profile, friend_profile

def get_status(user_profile: UserProfile, friend: User) -> str:
    """
    Function take UserProfile of one user and User of another.
    Returns status of the second one to first one. 
    """
    status = "Nothing"
    if user_profile.user.username == friend.username:
        return "We recognized you! It is your username"

    try:
        user_profile.friends.get(username=friend.username)
        return "Friends"
    except User.DoesNotExist:
        pass

    try:
        user_profile.requests.get(to_user=friend, status="pending")
        return "Request was sent"
    except FriendshipRequest.DoesNotExist:
        pass

    try:
        user_profile.requests.get(from_user=friend, status="pending")
        return "User is waiting you to answer on the friendship request"
    except FriendshipRequest.DoesNotExist:
        pass
    
    return status

def change_status_of_request(from_user: UserProfile, to_user: UserProfile, new_stat: str, old_stat: str = "pending"):
   """
   Internal function gets user is sending request, user is getting request, status to be set and old status
   (required when not 'pending', 'pending' default)
   """
   try:
        from_user_req =  from_user.requests.get(to_user=to_user.user.id, status=old_stat)
   except FriendshipRequest.DoesNotExist:
        from_user_req =  from_user.requests.get(from_user=to_user.user.id, status=old_stat)

   try:
        to_user_req = to_user.requests.get(from_user=from_user.user.id, status=old_stat)
   except FriendshipRequest.DoesNotExist:
        to_user_req = to_user.requests.get(to_user=from_user.user.id, status=old_stat)

   from_user_req.status = new_stat
   to_user_req.status = new_stat

   from_user_req.save()
   to_user_req.save()