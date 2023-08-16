import json
from datetime import datetime

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

import os

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

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json['username']
        await database_sync_to_async(self.save_message)(content=message,chat_id=self.scope["url_route"]["kwargs"]["room_name"])

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message, 'username': username,}
        )

    def save_message(self, content, chat_id):
        Messages.objects.create(user=self.scope["user"], content=content, chat_id=chat_id)

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        username = event['username']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message, 'username': username, 'time': timezone.now().strftime('%H:%M')}))