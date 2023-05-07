from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import django.contrib.auth as auth

from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import FriendshipRequest
from .serializers import UserSerializer, get_requests_serialized
from.forms import FriendshipForm
from users.models import UserProfile, User
from .tools import get_status, get_user_friend_profiles, accept_request, change_status_of_request


@login_required
def index(request):
    """main page with list of available actions with friendship"""
    return render(request, "index.html")


@login_required
@api_view(('GET',))
def show_friends(request):
    """show_friends returns drf response with current username and its friends"""
    user = UserProfile.objects.get(user=auth.get_user(request))
    friends = UserSerializer(user.friends.all(), many=True).data

    # return render(request, "friends.html", {'friends': friends})
    return Response({"friends": friends})

@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING, description="username of user to be checked"),
        }
    ),
)
@login_required
@api_view(("GET", "POST"))
def check_status(request):
    """check_status is provided for user to get information about connection with other user"""
    if request.method == "POST":
        # form = FriendshipForm(request.POST)
        user_profile = UserProfile.objects.get(user=auth.get_user(request))

        try:
            friend = User.objects.get(username=request.data["username"])
        except User.DoesNotExist:
            return Response("User doesn't exist", 400)
        
        status = get_status(user_profile, friend)

    else:
        status = ""
        form = FriendshipForm()
        # wanna return to website? place this return except lower one
        return render(request, 'check_status.html', {'form': form, 'status': status})

    return Response(status, 200)

@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING, description="username of user to be added"),
        }
    ),
)
@login_required()
@api_view(("POST", "GET"))
def add_friend(request):
    """
    add_friend in case of GET write form of friend search,
    in case of POST, gets username from request body check if user exists.
    Then it sends request of friendship
    """
    user_profile = UserProfile.objects.get(user=auth.get_user(request))

    if request.method == 'POST':
        try:
            friend = User.objects.get(username=request.data["username"])
            friend_profile = UserProfile.objects.get(user=friend)
        except User.DoesNotExist:
            return Response("User doesn't exist", status=400)
        
        # checking if users are already friends or request of friendship was already sent
        if friend not in user_profile.friends.all() and user_profile.user.id != friend.id:
            incoming, outcoming = get_requests_serialized(user_profile)

            for freq in outcoming:
                if freq["to_user"] == friend.id:
                    return Response("Already sent", status=400)
                    
            for freq in incoming:          
                if freq["from_user"] == friend.id:
                    accept_request(friend_profile, user_profile)
                    return Response("Now you are friends!")
                
            fs_request = FriendshipRequest(from_user=user_profile.user, to_user=friend)
            fs_request.save()
            user_profile.requests.add(fs_request)
            friend_profile.requests.add(fs_request)

            # return redirect("show_requests")
            return Response("Request was sent", 200)
            
        else:
            return Response("Already freinds", status=400)
    else:
        form = FriendshipForm()
    return render(request, 'add_friend.html', {'form': form, 'user':str(user_profile)})
    
@login_required
@api_view(("GET",))
def show_requests(request):
    """
    List all incoming and outcoming requests with status pending for current user
    """
    user = UserProfile.objects.get(user=auth.get_user(request))
    incoming, outcoming = get_requests_serialized(user)

    return Response({
        "user": str(user),
        "outcoming": outcoming,
        "incoming": incoming
    })

    # return render(request, "requests.html", {
    #     "user": str(user),
    #     "outcoming": outcoming,
    #     "incoming": incoming
    # })

@swagger_auto_schema(
    method="put",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "to_user": openapi.Schema(type=openapi.TYPE_INTEGER, description="id of user to whom you wanna withdraw request"),
        }
    ),
)
@login_required
@api_view(("PUT",))
def withdraw(request):
    """
    Withdraw of friendship request. Gets user id to whom request was sent to be withdrawed."""
    friend_id = request.data["to_user"]

    user_profile, friend_profile = get_user_friend_profiles(request, friend_id)
    change_status_of_request(user_profile, friend_profile, 'withdrawed')

    return Response("request was withdrawed")
    # return redirect("show_requests")

@swagger_auto_schema(
    method="put",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "to_user": openapi.Schema(type=openapi.TYPE_INTEGER, description="id of user from whom you wanna accept request"),
        }
    ),
)
@login_required
@api_view(("PUT",))
def accept(request):
    """
    Acceptance of friendship request. Gets id of user to be accepted as friend"""
    friend_id = request.data["from_user"]

    user_profile, friend_profile = get_user_friend_profiles(request, friend_id)
    accept_request(friend_profile, user_profile)

    return Response("now you are friends")
    # return redirect("show_requests")

@swagger_auto_schema(
    method="put",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "to_user": openapi.Schema(type=openapi.TYPE_INTEGER, description="id of user from whom you wanna reject request"),
        }
    ),
)
@login_required
@api_view(("PUT",))
def reject(request):
    """
    Rejection of friendship request. Get user id of sender of the request to be rejected."""
    friend_id = request.data["from_user"]

    user_profile, friend_profile = get_user_friend_profiles(request, friend_id)

    change_status_of_request(friend_profile, user_profile, "reject")
    # return redirect("show_requests")
    return Response("request was rejected")

@swagger_auto_schema(
    method="delete",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "from_user": openapi.Schema(type=openapi.TYPE_STRING, description="username of user to be deleted from your friends"),
        }
    ),
)
@login_required
@api_view(("DELETE",))
def delete_friend(request):
    """
    Deleting friend. Get username of user to be deleted from friends"""
    friend = User.objects.get(username=request.data["from_user"])
    friend_profile = UserProfile.objects.get(user=friend)

    user_profile = UserProfile.objects.get(user=auth.get_user(request))
    friend_profile.friends.remove(user_profile.user)
    user_profile.friends.remove(friend)

    change_status_of_request(friend_profile, user_profile, "reject", "accepted")

    # return redirect("show_friends")
    return Response(f"friend {friend.username} was deleted")

@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "to_user": openapi.Schema(type=openapi.TYPE_INTEGER, description="id of user to send hello"),
        }
    ),
)
@login_required
@api_view(("POST", ))
def send_message(request):
    """Sends hello to user with id user_id"""
    user_id = request.data["to_user"]
    return Response({"message":"Hello!", "to_user":user_id})


