from django.shortcuts import render, redirect
from django.http import JsonResponse

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import django.contrib.auth as auth

from .models import UserProfile
from .forms import LoginForm, SignupForm


def index(request):
    """index renders main page template"""
    return render(request, "users/index.html")

def user_login(request):
    """User login function. In case of GET write form, in case of POST authenticate user"""
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            user = auth.authenticate(username=cd['username'], password=cd['password'])

            if user is not None:
                print(user.id)
                if user.is_active:
                    auth.login(request, user)

                    return redirect("friendship/")
                else:
                    return JsonResponse({'message':'Disabled account'})
            else:
                return JsonResponse({'message':'Invalid login or password'})
    else:
        form = LoginForm()
    
    return render(request, 'users/login.html', {'form': form})

def user_signup(request):
    """User signup function. In case of GET write form, in case of POST and in case of form matching, signing up user"""
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save()
            user_profile = UserProfile.objects.create(user=user)
            user_profile.save()

            auth.login(request, user)

            return redirect("friendship/")
        else:
            return JsonResponse(form.error_messages)
            
    else:
        form = SignupForm()

    return render(request, 'users/signup.html', {'form': form})

@login_required()
def user_logout(request):
    """User log out function"""
    auth.logout(request)
    return redirect("login/")