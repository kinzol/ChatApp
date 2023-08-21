from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import *

class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Login', widget=forms.TextInput(attrs={'placeholder': 'Login', 'class': 'auth-input'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'auth-input'}))


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Login', widget=forms.TextInput(attrs={'placeholder': 'Login', 'class': 'auth-input'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'auth-input'}))
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'auth-input'}))
    password2 = forms.CharField(label='Password repeat', widget=forms.PasswordInput(attrs={'placeholder': 'Password again :D', 'class': 'auth-input'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class SettingsForm(forms.ModelForm):
    bio = forms.CharField(max_length=255, label='Bio', widget=forms.Textarea(attrs={'placeholder': 'Your bio', 'class': 'settings-change-bio'}))
    avatar = forms.ImageField(label='Avatar')

    class Meta:
        model = Profile
        fields = ('bio', 'avatar')