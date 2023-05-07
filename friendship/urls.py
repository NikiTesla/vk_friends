from . import views

from django.urls import path

urlpatterns = [
    path("", views.index, name="friendship_index"),
    path("show_friends", views.show_friends, name="show_friends"),
    path("add_friend", views.add_friend, name="add_friend"),
    path("show_requests", views.show_requests, name="show_requests"),
    path("check_status", views.check_status, name="check_status"),

    path("accept", views.accept, name="accept"),
    path("reject", views.reject, name="reject"),
    path("withdraw", views.withdraw, name="withdraw"),

    path("delete_friend", views.delete_friend, name="delete_friend"),
    path("send_message", views.send_message, name="send_message")
]