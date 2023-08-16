from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView

from .models import *
from .forms import *


class MainMenu(LoginRequiredMixin, TemplateView):
    template_name = 'chat/index.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = {"title": f"Main Menu", 'chats': self.get_chats()}
        return dict(list(context.items()) + list(c_def.items()))

    def get_chats(self):
        chats = Chat.objects.filter(Q(user1=self.request.user.id) | Q(user2=self.request.user.id))
        list_chats = []

        for chat in chats:
            try:
                message = Messages.objects.filter(chat_id=chat.pk).order_by('-id')[:1][0]
                list_chats.append([chat, message])
            except Exception:
                list_chats.append([chat, []])

        return list_chats



class ChatPage(LoginRequiredMixin, TemplateView):
    template_name = 'chat/chatPage.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        user, messages = self.get_messages_info(kwargs['room_name'])

        context = super().get_context_data(**kwargs)
        c_def = {'room_name': kwargs['room_name'], "title": f"Chat with {user}", 'mate_user': user, 'messages': messages, 'chats': self.get_chats()}
        return dict(list(context.items()) + list(c_def.items()))


    def get_messages_info(self, room_name):
        chats = Chat.objects.get(pk=room_name)
        if self.request.user.id == chats.user1.id or self.request.user.id == chats.user2.id:
            messages = Messages.objects.filter(chat_id=room_name)

        if self.request.user.id == chats.user1.id:
            user = chats.user2
        else:
            user = chats.user1

        return user, messages

    def get_chats(self):
        chats = Chat.objects.filter(Q(user1=self.request.user.id) | Q(user2=self.request.user.id))
        list_chats = []

        for chat in chats:
            try:
                message = Messages.objects.filter(chat_id=chat.pk).order_by('-id')[:1][0]
                list_chats.append([chat, message])
            except Exception:
                list_chats.append([chat, []])
        return list_chats


class SearchUsers(LoginRequiredMixin, ListView):
    model = User
    template_name = 'chat/search_users.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        result = self.get_search_result(self.kwargs['search_name'])

        context = super().get_context_data(**kwargs)
        c_def = {"title": f"Search result: {self.kwargs['search_name']}", 'search_result': result}
        return dict(list(context.items()) + list(c_def.items()))

    def get_search_result(self, search_name):
        result = User.objects.filter(Q(username__icontains=search_name))
        return result

@login_required(login_url='login')
def new_chat(request, id_user):
    mate = User.objects.get(pk=id_user)

    if request.user.id != mate.id:
        chats = Chat.objects.filter((Q(user1=request.user) | Q(user2=request.user)) & (Q(user1=mate) | Q(user2=mate)))
        if not chats:
            new_chat = Chat(user1=request.user, user2=mate)
            new_chat.save()
            return redirect(f'/chat/{new_chat.id}')
        else:
            return redirect(f'/chat/{chats[0].id}')
    return redirect('home')


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

