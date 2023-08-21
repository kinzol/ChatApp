import asyncio
import json
from datetime import datetime

from asgiref.sync import sync_to_async, async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

import os

from django.db.models import Q
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatApp.settings')
import django
django.setup()

from .models import *

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await database_sync_to_async(self.change_all_messages_status)(chat_id=self.scope["url_route"]["kwargs"]["room_name"])
        await self.channel_layer.group_send(self.room_group_name, {"type": "chat.read", 'is_connect': True,'from_user': str(self.scope['user'])})


    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json['username']
        await database_sync_to_async(self.save_message)(content=message,chat_id=self.scope["url_route"]["kwargs"]["room_name"], )

        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message, 'username': username,}
        )

    def save_message(self, content, chat_id):
        Messages.objects.create(user=self.scope["user"], content=content, chat_id=chat_id)

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        username = event['username']
        await self.send(text_data=json.dumps({"message": message, 'username': username, 'time': timezone.now().strftime('%H:%M')}))

        status = await database_sync_to_async(self.change_message_status)(chat_id=self.scope["url_route"]["kwargs"]["room_name"])
        if status:
            await self.channel_layer.group_send(self.room_group_name, {"type": "chat.read", 'is_connect': False, 'from_user': '0'})

    async def chat_read(self, event):
        await self.send(text_data=json.dumps({'status_read': True, 'is_connect': event['is_connect'], 'from_user': event['from_user']}))

    def change_message_status(self, chat_id):
        last_message = Messages.objects.filter(chat_id=chat_id).order_by('-id')[:1][0]
        if str(self.scope['user']) != last_message.user.username:
            last_message.read = True
            last_message.save()
            return True
        return False


    def change_all_messages_status(self, chat_id):
        last_messages = Messages.objects.filter(Q(chat_id=chat_id) & ~Q(user=self.scope['user']))

        for last_message in last_messages:
            last_message.read = True
            last_message.save()




class GeneralConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = "general"
        self.room_group_name = f"chat"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await database_sync_to_async(self.change_user_online_status)(online_status=True)
        last_online = await sync_to_async(lambda: self.scope['user'].profile.last_online)()
        await self.channel_layer.group_send(self.room_group_name,{"type": "chat.online", "status_online": True,
                                                                  'last_online': str(last_online.strftime('%d %B, %H:%M')),
                                                                  'from_user': self.scope['user'].pk})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await database_sync_to_async(self.change_user_online_status)(online_status=False)
        await asyncio.sleep(1)
        status = await database_sync_to_async(self.check_user_online_status)()

        if not status:
            last_online = await sync_to_async(lambda: self.scope['user'].profile.last_online)()
            await self.channel_layer.group_send(self.room_group_name,{"type": "chat.online", "status_online": False,
                                                                      'last_online': str(last_online.strftime('%d %B, %H:%M')),
                                                                      'from_user': self.scope['user'].pk})

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        from_chat = text_data_json["from_chat"]
        to_user = text_data_json['to_user']

        await self.channel_layer.group_send(self.room_group_name, {"type": "chat.message", "from_chat": from_chat, 'to_user': to_user, })

    # Receive message from room group
    async def chat_message(self, event):
        from_chat = event["from_chat"]
        to_user = event['to_user']
        await self.send(text_data=json.dumps({"from_chat": from_chat, 'to_user': to_user, 'time': timezone.now().strftime('%H:%M')}))

    async def chat_online(self, event):
        status_online = event['status_online']
        last_online = event['last_online']
        from_user = event['from_user']
        await self.send(text_data=json.dumps({"from_user": from_user, "status_online": status_online, 'last_online': last_online}))

    def change_user_online_status(self, online_status):
        user_profile = Profile.objects.get(user=self.scope['user'])
        user_profile.status_online = online_status
        user_profile.save()

    def check_user_online_status(self):
        user_profile = Profile.objects.get(user=self.scope['user'])
        return user_profile.status_online