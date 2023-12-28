from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *


class ChatAdmin(admin.ModelAdmin):
    list_display = ("id", 'display_participants', 'time_create')
    list_display_links = ('id', 'display_participants', 'time_create')
    filter_horizontal = ('participants',)

    def display_participants(self, obj):
        return ', '.join([participant.username for participant in obj.participants.all()])


class GroupAdmin(admin.ModelAdmin):
    list_display = ("id", 'root', 'name', 'get_html_photo', 'display_participants',
                    'display_admins', 'bio', 'time_create')
    list_display_links = ("id", 'root', 'name', 'get_html_photo', 'display_participants',
                          'display_admins', 'bio', 'time_create')
    filter_horizontal = ('participants', 'admins')

    def display_participants(self, obj):
        return ', '.join([participant.username for participant in obj.participants.all()])

    def display_admins(self, obj):
        return ', '.join([admins.username for admins in obj.admins.all()])

    def get_html_photo(self, object):
        if object.avatar:
            return mark_safe(f"<img src='{object.avatar.url}' width=50>")

    get_html_photo.short_description = "Avatar"


class MessagesAdmin(admin.ModelAdmin):
    list_display = ("id", 'user', 'content', 'time_create', 'read', 'chat_id')
    list_display_links = ("id", 'user', 'content', 'time_create', 'read', 'chat_id')
    search_fields = ('user',)


class GroupMessagesAdmin(admin.ModelAdmin):
    list_display = ("id", 'user', 'content', 'time_create', 'chat_id')
    list_display_links = ("id", 'user', 'content', 'time_create', 'chat_id')
    search_fields = ('user',)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", 'get_html_photo', 'user', 'status_online', 'last_online', 'bio')
    list_display_links = ("id", 'get_html_photo', 'user', 'status_online', 'last_online', 'bio')
    search_fields = ('user',)

    def get_html_photo(self, object):
        if object.avatar:
            return mark_safe(f"<img src='{object.avatar.url}' width=50>")

    get_html_photo.short_description = "Avatar"


admin.site.register(Chat, ChatAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Messages, MessagesAdmin)
admin.site.register(GroupMessages, GroupMessagesAdmin)
admin.site.register(Profile, ProfileAdmin)
