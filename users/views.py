from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import django.contrib.auth as auth

from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import UserProfile, User
from .forms import LoginForm, SignupForm

def index(request):
    """index renders main page template"""
    return render(request, "users/index.html")

@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING),
            "password": openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
)
@api_view(("GET", "POST"))
def user_login(request):
    """User login function. In case of GET write form, in case of POST authenticate user"""
    if request.method == 'POST':
        # form = LoginForm(request.POST)

        # if form.is_valid():
        #     cd = form.cleaned_data
        #     user = auth.authenticate(username=cd['username'], password=cd['password'])
        try:
            username = request.data["username"]
            password = request.data["password"]
        except KeyError:
            return Response("You should propose both username and password fields")
        
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                auth.login(request, user)

                # return redirect("friendship/")
                return Response("Logged in successfully")
            else:
                return Response("Disabled account")
        else:
            return Response("Invalid login or password")
    else:
        form = LoginForm()
        return render(request, 'users/login.html', {'form': form})

@swagger_auto_schema(
    method="post",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING),
            "password1": openapi.Schema(type=openapi.TYPE_STRING),
            "password2": openapi.Schema(type=openapi.TYPE_STRING, description="password confirmation"),
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="in format of email *@*.*")
        }
    ),
)
@api_view(("GET", "POST"))
def user_signup(request):
    """
    User signup function. In case of GET renders html template with signup form.
    In case of POST call request body parse function, create user with parameters and log in

    """
    if request.method == 'POST':
        # form = SignupForm(request.POST)

        # if form.is_valid():
        #     user = form.save()
        # else:
        #     return Response(form.error_messages)

        user = parse_signup(request)
        if type(user) is Response:
            return user
        
        user.save()
        user_profile = UserProfile.objects.create(user=user)
        user_profile.save()

        auth.login(request, user)
        return Response("You was signed up and logged in")
            
    else:
        form = SignupForm()

    return render(request, 'users/signup.html', {'form': form})

@login_required()
@api_view(("GET",))
def user_logout(request):
    """User log out function"""
    auth.logout(request)
    # return redirect("login/")
    return Response("You were logged out", 200)


def parse_signup(request) -> User | Response:
    """
    Function that parses request body with username, email, password1 and confirmation password2.
    Create and return django.contrib.auth.models.User and returns it. 
    """
    username = request.data["username"]
    password1 = request.data["password1"]
    password2 = request.data["password2"]
    email = request.data["email"]

    if password1 != password2:
        return Response("Passwords are different", status=400)
    if len(username) < 6 or len(password1) < 8:
        return Response("Username should contain 6 or more symbols. Password should contain 8 or more symbols", 400)
    if "@" not in email or len(email) < 6:
        return Response("Email is incorrect", 400)
    try:
        User.objects.get(username=username)
        return Response("Username already exists", 400)
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, email=email, password=password1)

    
    return user