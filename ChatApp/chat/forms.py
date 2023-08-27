from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import *

class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Login', widget=forms.TextInput(attrs={'placeholder': 'Login', 'class': 'auth-input'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'auth-input'}))


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(max_length=13, label='Login', widget=forms.TextInput(attrs={'placeholder': 'Login', 'class': 'auth-input'}))
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

class CreateGroupForm(forms.ModelForm):
    name = forms.CharField(max_length=13, label='Group-name', widget=forms.TextInput(attrs={'placeholder': f'Group name', 'class': 'group-name'}))
    bio = forms.CharField(max_length=255, required=False, label='Bio',widget=forms.Textarea(attrs={'placeholder': 'Group bio', 'class': 'group-bio'}))
    avatar = forms.ImageField(label='Avatar', required=False)
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'create-group-many-to-many'})
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')

        super(CreateGroupForm, self).__init__(*args, **kwargs)
        chats = Chat.objects.filter(participants=self.request.user)
        users_in_chats = []

        for chat in chats:
            users_in_chat = chat.participants.all()
            users_in_chats.extend(users_in_chat)

        participants_queryset = User.objects.filter(pk__in=[user.id for user in users_in_chats if user != self.request.user]).distinct()
        self.fields['participants'].queryset = participants_queryset

    class Meta:
        model = Group
        fields = ('name', 'avatar', 'bio')


class AddUserGroupForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'group-add-new-user'})
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.from_group = kwargs.pop('from_group')

        super(AddUserGroupForm, self).__init__(*args, **kwargs)
        chats = Chat.objects.filter(participants=self.request.user)
        group = Group.objects.get(pk=self.from_group)
        group_member = group.participants.all()
        users_in_chats = []

        for chat in chats:
            users_in_chat = chat.participants.all()
            users_in_chats.extend(users_in_chat)

        participants_queryset = User.objects.filter(pk__in=[user.id for user in users_in_chats if user != self.request.user and not user in group_member]).distinct()
        self.fields['participants'].queryset = participants_queryset

    class Meta:
        model = Group
        fields = tuple()


class GroupEditForm(forms.ModelForm):
    name = forms.CharField(max_length=13, widget=forms.TextInput(attrs={'placeholder': f'Group name'}))
    bio = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'placeholder': 'Group bio'}))
    avatar = forms.ImageField(label='Avatar', required=False)

    class Meta:
        model = Group
        fields = ('name', 'avatar', 'bio')