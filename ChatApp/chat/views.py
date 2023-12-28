from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView
from django.views.generic.edit import FormMixin, UpdateView

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

        c_def = self.get_user_context(room_name=kwargs['room_name'], title=f"Chat with {user}",
                                      mate_user=user, messages=messages, type_page='chat')

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


class GroupPage(DataMixin, LoginRequiredMixin, TemplateView):
    template_name = 'chat/groupPage.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        group_name, messages, group_users = self.get_messages_info(kwargs['room_name'])
        context = super().get_context_data(**kwargs)

        c_def = self.get_user_context(room_name=kwargs['room_name'], title=f"Group {group_name}",
                                      group_name=group_name, messages=messages, group_users=group_users,
                                      type_page='group')

        return dict(list(context.items()) + list(c_def.items()))

    def get_messages_info(self, room_name):
        group = Group.objects.get(pk=room_name)
        group_users = group.participants.all()
        if self.request.user in group_users:
            messages = GroupMessages.objects.filter(chat_id=room_name)
            return group.name, messages, group_users
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


def delete_message(request, message_id, from_chat):
    message = Messages.objects.get(pk=message_id)
    if message.user == request.user:
        message.delete()
    return redirect('chat-page', room_name=from_chat)


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


class CreateGroup(LoginRequiredMixin, CreateView, DataMixin):
    model = Group
    template_name = 'chat/create_group.html'
    form_class = CreateGroupForm
    success_url = reverse_lazy('home')
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=f"New group",)
        return dict(list(context.items()) + list(c_def.items()))

    def get_form_kwargs(self):
        kwargs = super(CreateGroup, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)

    def form_valid(self, form):
        self.object = form.save()
        self.object.root = self.request.user
        participants = form.cleaned_data.get('participants')
        self.object.participants.set(participants)
        self.object.participants.add(self.request.user)
        self.object.save()
        return super().form_valid(form)


class GroupInfo(LoginRequiredMixin, DataMixin, TemplateView, FormMixin):
    template_name = 'chat/group_info.html'
    form_class = GroupEditForm
    success_url = reverse_lazy('home')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)

    def form_valid(self, form):
        self.object = form.save()
        self.object.save()
        return redirect('group-info', room_name=self.kwargs['room_name'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        instance = Group.objects.get(pk=self.kwargs['room_name'])
        kwargs['instance'] = instance
        return kwargs

    def get_context_data(self, **kwargs):
        group, group_users, group_admins = self.get_group_info(kwargs['room_name'])
        context = super().get_context_data(**kwargs)

        c_def = self.get_user_context(room_name=kwargs['room_name'], title=f"Group information {group.name}",
                                      group=group, group_users=group_users, group_admins=group_admins)

        return dict(list(context.items()) + list(c_def.items()))

    def get_group_info(self, room_name):
        group = Group.objects.get(pk=room_name)
        group_users = group.participants.all()
        group_admins = group.admins.all()

        if self.request.user in group_users:

            return group, group_users, group_admins
        else:
            redirect('home')


@login_required(login_url='login')
def group_give_admin(request, user, from_group):
    group = Group.objects.get(pk=from_group)
    group_admin = group.admins.all()
    selected_user = User.objects.get(pk=user)
    if request.user == group.root and selected_user not in group_admin:
        group.admins.add(selected_user)
        group.save()
    return redirect("group-info", room_name=from_group)


@login_required(login_url='login')
def group_remove_admin(request, user, from_group):
    group = Group.objects.get(pk=from_group)
    group_admin = group.admins.all()
    selected_user = User.objects.get(pk=user)
    if request.user == group.root and selected_user in group_admin:
        group.admins.remove(selected_user)
        group.save()
    return redirect("group-info", room_name=from_group)


@login_required(login_url='login')
def group_kick(request, user, from_group):
    group = Group.objects.get(pk=from_group)
    group_admin = group.admins.all()
    selected_user = User.objects.get(pk=user)

    is_not_selected_user = request.user != selected_user
    is_root_user = request.user == group.root
    is_user_admin = request.user in group_admin
    is_selected_user_not_admin = selected_user not in group_admin

    if is_not_selected_user and (is_root_user or (is_user_admin and is_selected_user_not_admin)):
        group.participants.remove(selected_user)
        if selected_user in group_admin:
            group.admins.remove(selected_user)
        group.save()
        return redirect("group-info", room_name=from_group)

    if request.user == selected_user and group.root != request.user:
        group.participants.remove(selected_user)
        if selected_user in group_admin:
            group.admins.remove(selected_user)
        group.save()
        return redirect("home")

    group_member = group.participants.all()
    print(group_member)
    if request.user == group.root and len(group_member) == 1:
        group.participants.remove(selected_user)
        group.save()
        return redirect("home")

    return redirect("group-info", room_name=from_group)


class GroupAdd(LoginRequiredMixin, DataMixin, TemplateView, FormMixin):
    template_name = 'chat/group_add_users.html'
    form_class = AddUserGroupForm
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        group = Group.objects.get(pk=self.kwargs['from_group'])
        group_members = group.participants.all()
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=f"Group {group.name}", group_name=group.name,
                                      group=group, group_members=group_members)
        return dict(list(context.items()) + list(c_def.items()))

    def get_form_kwargs(self):
        kwargs = super(GroupAdd, self).get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['from_group'] = self.kwargs['from_group']
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)

    def form_valid(self, form):
        group = Group.objects.get(pk=self.kwargs['from_group'])

        participants = form.cleaned_data.get('participants')
        for user in participants:
            group.participants.add(user)
        group.save()
        return redirect('group-info', room_name=self.kwargs['from_group'])


# auth
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
