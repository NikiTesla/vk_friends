from django import forms

class FriendshipForm(forms.Form):
    username = forms.CharField(max_length=100)