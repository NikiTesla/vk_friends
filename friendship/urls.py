from . import views

from django.urls import path

urlpatterns = [
    path("", views.index, name="friendship_index"),
    path("show_friends", views.show_friends, name="show_friends"),
    path("add_friend", views.add_friend, name="add_friend"),
    path("show_requests", views.show_requests, name="show_requests"),
    path("accept", views.accept, name="accept"),
    path("reject", views.reject, name="reject"),
    path("withdraw", views.withdraw, name="withdraw"),
]