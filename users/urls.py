from . import views

from django.urls import path

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login, name="user_login"),
    path("signup", views.signup, name="user_signup"),
    path("users_list", views.list_users, name="list_users"),
    # path("friendship_requests", views.friendship_requests, name="friendship_requests")
]