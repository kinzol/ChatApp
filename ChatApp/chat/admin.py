from django.contrib import admin

# Register your models here.
from .models import *

class ChatAdmin(admin.ModelAdmin):
    list_display = ("id", 'user1', 'user2', 'time_create')
    list_display_links = ('id', 'user1', 'user2', 'time_create')
    search_fields = ('user1',)


class MessagesAdmin(admin.ModelAdmin):
    list_display = ("id", 'user', 'content', 'time_create', 'read', 'chat_id')
    list_display_links = ("id", 'user', 'content', 'time_create', 'read', 'chat_id')
    search_fields = ('user',)


admin.site.register(Chat, ChatAdmin)
admin.site.register(Messages, MessagesAdmin)