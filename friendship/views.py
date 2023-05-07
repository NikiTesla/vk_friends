from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import django.contrib.auth as auth
from django.contrib.auth.models import User

from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import FriendshipRequest
from.forms import FriendshipForm
from users.models import UserProfile
from .serializers import UserSerializer, get_requests_serialized

class SkipException(Exception):
    """Exception for skip blocks of code with status message"""
    def __init__(self, status: str=""):
        self.status = status

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

    return render(request, "friends.html", {'friends': friends})

@login_required
@api_view(("GET", "POST"))
def check_status(request):
    """check_status is provided for user to get information about connection with other user"""
    try:
        assert request.method == "POST"
        form = FriendshipForm(request.POST)
        user_profile = UserProfile.objects.get(user=auth.get_user(request))

        if form.is_valid():
            cd = form.cleaned_data
            try:
                friend = User.objects.get(username=cd['username'])
            except User.DoesNotExist:
                return Response("User doesn't exist")
        
        status = "Nothing"
        try:
            if user_profile.user.username == friend.username:
                status = "We recognized you! It is your username"
                raise SkipException(status)
            
            user_profile.friends.get(username=friend.username)
            status = "Friends"
            raise SkipException(status)
        except User.DoesNotExist:
            pass

        try:
            user_profile.requests.get(to_user=friend, status="pending")
            status = "Request was sent"
            raise SkipException(status)
        except FriendshipRequest.DoesNotExist:
            pass

        try:
            user_profile.requests.get(from_user=friend, status="pending")
            status = "User is waiting you to answer on the friendship request"
            raise SkipException(status)
        except FriendshipRequest.DoesNotExist:
            pass

    except AssertionError:
        status = ""
        form = FriendshipForm()
    except SkipException as e:
        form = ""
        status = e.status

    return render(request, 'check_status.html', {'form': form, 'status': status})

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
                incoming, outcoming = get_requests_serialized(user_profile)
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
    
    return render(request, 'add_friend.html', {'form': form, 'user':str(user_profile)})

@login_required
@api_view(("GET",))
def show_requests(request):
    """list all incoming and outcoming requests with status pending for current user"""
    user = UserProfile.objects.get(user=auth.get_user(request))
    incoming, outcoming = get_requests_serialized(user)

    return render(request, "requests.html", {
        "user": str(user),
        "outcoming": outcoming,
        "incoming": incoming
    })

@login_required
@api_view(("POST",))
def withdraw(request):
    """withdraw of friendship request"""
    if request.method == "POST":
        friend_id = request.POST.get('to_user')

    user_profile, friend_profile = _get_user_friend_profiles(request, friend_id)
    _stat_request(user_profile, friend_profile, 'withdrawed')

    return redirect("show_requests")

@login_required
@api_view(("POST",))
def accept(request):
    """acceptance of friendship request"""
    if request.method == "POST":
        friend_id = request.POST.get('from_user')

    user_profile, friend_profile = _get_user_friend_profiles(request, friend_id)
    _accept_request(friend_profile, user_profile)

    return redirect("show_requests")

@login_required
@api_view(("POST",))
def reject(request):
    """rejection of friendship request"""
    if request.method == "POST":
        friend_id = request.POST.get('from_user')

    user_profile, friend_profile = _get_user_friend_profiles(request, friend_id)

    _stat_request(friend_profile, user_profile, "reject")
    return redirect("show_requests")

@login_required
@api_view(("POST",))
def delete_friend(request):
    """deleting friend"""
    if request.method == "POST":
        friend = User.objects.get(username=request.POST.get('from_user'))
        friend_profile = UserProfile.objects.get(user=friend)

        user_profile = UserProfile.objects.get(user=auth.get_user(request))

        friend_profile.friends.remove(user_profile.user)
        user_profile.friends.remove(friend)

        _stat_request(friend_profile, user_profile, "reject", "accepted")

    return redirect("show_friends")

@login_required
@api_view(("GET", "POST"))
def send_message(request):
    ...

def _accept_request(from_user: UserProfile, to_user: UserProfile):
    """internal function gets user is sending request, user is accepting request, makes them friends"""
    from_user.friends.add(to_user.user)
    to_user.friends.add(from_user.user)

    _stat_request(from_user, to_user, "accepted")
    
def _stat_request(from_user: UserProfile, to_user: UserProfile, new_stat: str, old_stat: str = "pending"):
   """internal function gets user is sending request, user is getting request and status to be set"""
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


def _get_user_friend_profiles(request, friend_id):
    """internal function that returns user_profile and friend_profile with id friend_id"""
    user_profile = UserProfile.objects.get(user=auth.get_user(request))

    friend = User.objects.get(id=friend_id)
    friend_profile = UserProfile.objects.get(user=friend)

    return user_profile, friend_profile