from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import django.contrib.auth as auth
from django.contrib.auth.models import User

from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import FriendshipRequest
from.forms import FriendshipForm
from users.models import UserProfile
from .serializers import UserSerializer, IncomeFriendshipRequestsSerializer, OutcomeFriendshipRequestsSerializer

@login_required
def index(request):
    return render(request, "friends/index.html")

@login_required()
@api_view(('GET',))
def show_friends(request):
    """show_friends returns drf response with current username and its friends"""
    user = UserProfile.objects.get(user=auth.get_user(request))
    friends = UserSerializer(user.friends.all(), many=True).data

    return render(request, "friends/friends.html", {'friends': friends})

@login_required()
@api_view(("POST","GET"))
def add_friend(request):
    """
    add_friend in case of GET write form of friend search,
    in case of POST, check if form is matchhed and if user exists.
    Then it sends request of friendship
    """
    user_profile = UserProfile.objects.get(user=auth.get_user(request))

    if request.method == 'POST':
        form = FriendshipForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            try:
                friend = User.objects.get(username=cd['username'])
                friend_profile = UserProfile.objects.get(user=friend)
            except User.DoesNotExist:
                return Response("User doesn't exist", status=400)
            
            if friend not in user_profile.friends.all() and user_profile.user.id != friend.id:
                incoming, outcoming = _get_requests_serialized(user_profile)
                for freq in outcoming:
                    if freq["to_user"] == friend.id:
                        return Response("Already sent", status=400)          
                for freq in incoming:          
                    if freq["from_user"] == friend.id:
                        _accept_request(friend_profile, user_profile)
                        return Response("Now you are friends!")
                    
                fs_request = FriendshipRequest(from_user=user_profile.user, to_user=friend)
                fs_request.save()
                user_profile.requests.add(fs_request)
                friend_profile.requests.add(fs_request)

                return redirect("show_requests")
                
            else:
                return Response("Already freinds", status=400)
    else:
        form = FriendshipForm()
    
    return render(request, 'friends/add_friend.html', {'form': form, 'user':str(user_profile)})

@login_required
@api_view(("GET",))
def show_requests(request):
    user = UserProfile.objects.get(user=auth.get_user(request))
    incoming, outcoming = _get_requests_serialized(user)

    return render(request, "friends/requests.html", {
        "user": str(user),
        "outcoming": outcoming,
        "incoming": incoming
    })

@api_view(("POST",))
def withdraw(request):
    """withdraw of friendship request"""
    if request.method == "POST":
        friend_id = request.POST.get('to_user')

    user_profile, friend_profile = _get_user_friend_profiles(request, friend_id)
    _stat_request(user_profile, friend_profile, 'withdrawed')

    return redirect("show_requests")

@api_view(("POST",))
def accept(request):
    """acceptance of friendship request"""
    if request.method == "POST":
        friend_id = request.POST.get('from_user')

    user_profile, friend_profile = _get_user_friend_profiles(request, friend_id)
    _accept_request(friend_profile, user_profile)

    return redirect("show_friends")

@api_view(("POST",))
def reject(request):
    """rejection of friendship request"""
    if request.method == "POST":
        friend_id = request.POST.get('from_user')

    user_profile, friend_profile = _get_user_friend_profiles(request, friend_id)

    _stat_request(friend_profile, user_profile, "reject")
    return redirect("show_requests")

def _get_requests_serialized(user: UserProfile):
    """Internal function to serialize incoming and outcoming requests for user"""
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


def _accept_request(from_user: UserProfile, to_user: UserProfile):
    """internal function gets user is sending request, user is accepting request, makes them friends"""
    from_user.friends.add(to_user.user)
    to_user.friends.add(from_user.user)

    _stat_request(from_user, to_user, "accepted")
    
def _stat_request(from_user: UserProfile, to_user: UserProfile, stat: str):
   """internal function gets user is sending request, user is getting request and status to be set"""
   from_user_req =  from_user.requests.get(to_user=to_user.user.id, status="pending")
   to_user_req = to_user.requests.get(from_user=from_user.user.id, status="pending")

   from_user_req.status = stat
   to_user_req.status = stat

   from_user_req.save()
   to_user_req.save()


def _get_user_friend_profiles(request, friend_id):
    """internal function that returns user_profile and friend_profile with id friend_id"""
    user_profile = UserProfile.objects.get(user=auth.get_user(request))

    friend = User.objects.get(id=friend_id)
    friend_profile = UserProfile.objects.get(user=friend)

    return user_profile, friend_profile