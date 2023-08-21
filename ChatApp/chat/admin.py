from django.contrib import admin
from django.utils.safestring import mark_safe

# Register your models here.
from .models import *

class ChatAdmin(admin.ModelAdmin):
    # list_display = ("id", 'user1', 'user2', 'time_create')participants
    list_display = ("id", 'display_participants', 'time_create')
    list_display_links = ('id', 'display_participants', 'time_create')
    # list_display_links = ('id', 'user1', 'user2', 'time_create')
    filter_horizontal = ('participants',)

    def display_participants(self, obj):
        return ', '.join([participant.username for participant in obj.participants.all()])


class MessagesAdmin(admin.ModelAdmin):
    list_display = ("id", 'user', 'content', 'time_create', 'read', 'chat_id')
    list_display_links = ("id", 'user', 'content', 'time_create', 'read', 'chat_id')
    search_fields = ('user',)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", 'get_html_photo', 'user', 'status_online', 'last_online', 'bio')
    list_display_links = ("id", 'get_html_photo', 'user', 'status_online', 'last_online', 'bio')
    search_fields = ('user',)

    def get_html_photo(self,object):
        if object.avatar:
            return mark_safe(f"<img src='{object.avatar.url}' width=50>")

    get_html_photo.short_description = "Avatar"


admin.site.register(Chat, ChatAdmin)
admin.site.register(Messages, MessagesAdmin)
admin.site.register(Profile, ProfileAdmin)