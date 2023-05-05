from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from .models import User
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignupForm


def index(request):
    return render(request, "users/index.html")

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    
    return render(request, 'users/login.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            
            try:
                user = User.objects.get(username=cd['username'])
            except User.DoesNotExist:
                user = User(username=cd['username'], password=cd['password'], email=cd['email'])
                user.save()
                return HttpResponse("Registered successfully")
            
            else:
                return HttpResponse("User with such username already exists")
        else:
            return HttpResponse("Invalid info")
            
    else:
        form = SignupForm()

    return render(request, 'users/signup.html', {'form': form})



def list_users(request):
    users = User.objects.all()

    if len(users) == 0:
        return HttpResponse("Users list is empty")

    return HttpResponse(" ".join([user.username for user in users]))