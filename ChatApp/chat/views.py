from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView
from django.views.generic.edit import FormMixin, UpdateView

from .models import *
from .forms import *

from .utils import *

class MainMenu(DataMixin, LoginRequiredMixin, TemplateView):
    template_name = 'chat/index.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=f"Main Menu")
        return dict(list(context.items()) + list(c_def.items()))



class ChatPage(DataMixin, LoginRequiredMixin, TemplateView):
    template_name = 'chat/chatPage.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        user, messages = self.get_messages_info(kwargs['room_name'])

        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(room_name=kwargs['room_name'], title=f"Chat with {user}", mate_user=user, messages=messages)
        return dict(list(context.items()) + list(c_def.items()))


    def get_messages_info(self, room_name):
        chat = Chat.objects.get(pk=room_name)
        chat_users = chat.participants.all()
        if self.request.user in chat_users:
            messages = Messages.objects.filter(chat_id=room_name)
            user = chat_users[0] if self.request.user != chat_users[0] else chat_users[1]
            return user, messages
        else:
            redirect('home')


class SearchUsers(DataMixin, LoginRequiredMixin, TemplateView):
    template_name = 'chat/search_users.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        result = self.get_search_result(self.kwargs['search_name'])

        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=f"Search result: {self.kwargs['search_name']}", search_result=result)
        return dict(list(context.items()) + list(c_def.items()))

    def get_search_result(self, search_name):
        result = User.objects.filter(Q(username__icontains=search_name) & ~Q(pk=self.request.user.id))
        return result

@login_required(login_url='login')
def new_chat(request, id_user):
    mate = User.objects.get(pk=id_user)

    if request.user != mate:
        chats_with_user = Chat.objects.filter(participants=request.user)
        chats = chats_with_user.filter(participants=mate)
        if not chats:
            new_chat = Chat.objects.create()
            new_chat.participants.add(request.user)
            new_chat.participants.add(mate)
            new_chat.save()
            return redirect(f'/chat/{new_chat.id}')
        else:
            return redirect(f'/chat/{chats[0].id}')
    return redirect('home')


class Settings(DataMixin, LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = SettingsForm
    template_name = 'chat/settings.html'
    login_url = 'login'
    success_url = reverse_lazy('settings')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=f"Settings", profile=self.get_data_profile())
        return dict(list(context.items()) + list(c_def.items()))

    def get_data_profile(self):
        return Profile.objects.get(user=self.request.user)


class UserProfile(DataMixin, LoginRequiredMixin, ListView):
    model = User
    template_name = 'chat/user_profile.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=f"Profile: {self.kwargs['username']}")
        return dict(list(context.items()) + list(c_def.items()))


    def get_queryset(self):
        queryset = User.objects.get(username=self.kwargs['username'])
        return queryset


#auth
class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = "chat/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = {'title': "Login"}
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self):
        return reverse_lazy('home')

class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'chat/registration.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = {'title': "Registration"}
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect("login")

