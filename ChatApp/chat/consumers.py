import asyncio
import json
import secrets
import string

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import *

import django
from django.db.models import Q
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatApp.settings')
django.setup()


class ChatConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = None
        self.room_group_name = None

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        chat_id = self.scope["url_route"]["kwargs"]["room_name"]
        await database_sync_to_async(self.change_all_messages_status)(chat_id=chat_id)
        await self.channel_layer.group_send(self.room_group_name, {"type": "chat.read", 'is_connect': True,
                                                                   'from_user': str(self.scope['user'])})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            letters_and_digits = string.ascii_letters + string.digits
            crypt_rand_string = ''.join(secrets.choice(letters_and_digits) for _ in range(10))
            file_name = fr'uploads\user_{self.scope["user"].pk}\audio'
            media_path = os.path.join('media', file_name)
            os.makedirs(media_path, exist_ok=True)
            media_path = os.path.join(media_path, f'message_{crypt_rand_string}.wav')

            await database_sync_to_async(self.save_audio)(content=media_path,
                                                          chat_id=self.scope["url_route"]["kwargs"]["room_name"], )

            with open(media_path, 'wb') as audio_file:
                audio_file.write(bytes_data)

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "chat.message", 'message_type': 'audio', "message": media_path,
                 'username': self.scope['user'].username}
            )

        if text_data:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            username = text_data_json['username']
            await database_sync_to_async(self.save_message)(content=message,
                                                            chat_id=self.scope["url_route"]["kwargs"]["room_name"], )

            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message",
                                       'message_type': 'text',
                                       "message": message,
                                       'username': username})

    def save_message(self, content, chat_id):
        Messages.objects.create(message_type='text', user=self.scope["user"], content=content, chat_id=chat_id)

    def save_audio(self, content, chat_id):
        new_message = Messages.objects.create(message_type='audio', user=self.scope["user"],
                                              content=content, chat_id=chat_id)
        return new_message.pk

    async def chat_message(self, event):
        message = event["message"]
        username = event['username']
        message_type = event['message_type']
        await self.send(text_data=json.dumps({'message_type': message_type, "message": message,
                                              'username': username, 'time': timezone.now().strftime('%H:%M')}))

        status = await database_sync_to_async(self.change_message_status)(
            chat_id=self.scope["url_route"]["kwargs"]["room_name"])
        if status:
            await self.channel_layer.group_send(self.room_group_name, {"type": "chat.read", 'is_connect': False,
                                                                       'from_user': '0'})

    async def chat_read(self, event):
        await self.send(text_data=json.dumps({'status_read': True, 'is_connect': event['is_connect'],
                                              'from_user': event['from_user']}))

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


class GroupConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = None
        self.room_group_name = None

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            letters_and_digits = string.ascii_letters + string.digits
            crypt_rand_string = ''.join(secrets.choice(letters_and_digits) for _ in range(10))
            file_name = fr'uploads\user_{self.scope["user"].pk}\audio'
            media_path = os.path.join('media', file_name)
            os.makedirs(media_path, exist_ok=True)
            media_path = os.path.join(media_path, f'message_{crypt_rand_string}.wav')

            await database_sync_to_async(self.save_audio)(content=media_path,
                                                          chat_id=self.scope["url_route"]["kwargs"]["room_name"], )

            with open(media_path, 'wb') as audio_file:
                audio_file.write(bytes_data)

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "chat.message", 'message_type': 'audio', "message": media_path,
                 'username': self.scope['user'].username, })

        if text_data:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            username = text_data_json['username']
            await database_sync_to_async(self.save_message)(content=message,
                                                            chat_id=self.scope["url_route"]["kwargs"]["room_name"], )

            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat.message", 'message_type': 'text', "message": message,
                                       'username': username})

    def save_message(self, content, chat_id):
        GroupMessages.objects.create(message_type='text', user=self.scope["user"], content=content, chat_id=chat_id)

    def save_audio(self, content, chat_id):
        new_message = GroupMessages.objects.create(message_type='audio', user=self.scope["user"], content=content,
                                                   chat_id=chat_id)
        return new_message.pk

    async def chat_message(self, event):
        message = event["message"]
        username = event['username']
        message_type = event['message_type']
        await self.send(text_data=json.dumps({'message_type': message_type, "message": message, 'username': username,
                                              'time': timezone.now().strftime('%H:%M')}))

        status = await database_sync_to_async(self.change_message_status)(
            chat_id=self.scope["url_route"]["kwargs"]["room_name"])

        if status:
            await self.channel_layer.group_send(self.room_group_name, {"type": "chat.read", 'is_connect': False,
                                                                       'from_user': '0'})

    async def chat_read(self, event):
        await self.send(text_data=json.dumps({'status_read': True, 'is_connect': event['is_connect'],
                                              'from_user': event['from_user']}))

    def change_message_status(self, chat_id):
        last_message = GroupMessages.objects.filter(chat_id=chat_id).order_by('-id')[:1][0]
        if str(self.scope['user']) != last_message.user.username:
            last_message.read = True
            last_message.save()
            return True
        return False

    def change_all_messages_status(self, chat_id):
        last_messages = GroupMessages.objects.filter(Q(chat_id=chat_id) & ~Q(user=self.scope['user']))

        for last_message in last_messages:
            last_message.read = True
            last_message.save()


class GeneralConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_name = None
        self.room_group_name = None

    async def connect(self):
        self.room_name = "general"
        self.room_group_name = f"chat"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await database_sync_to_async(self.change_user_online_status)(online_status=True)
        last_online = await sync_to_async(lambda: self.scope['user'].profile.last_online)()
        await self.channel_layer.group_send(self.room_group_name, {"type": "chat.online", "status_online": True,
                                                                   'last_online':
                                                                       str(last_online.strftime('%d %B, %H:%M')),
                                                                   'from_user': self.scope['user'].pk})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await database_sync_to_async(self.change_user_online_status)(online_status=False)
        await asyncio.sleep(1)
        status = await database_sync_to_async(self.check_user_online_status)()

        if not status:
            last_online = await sync_to_async(lambda: self.scope['user'].profile.last_online)()
            await self.channel_layer.group_send(self.room_group_name, {"type": "chat.online", "status_online": False,
                                                                       'last_online':
                                                                           str(last_online.strftime('%d %B, %H:%M')),
                                                                       'from_user': self.scope['user'].pk})

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        from_chat = text_data_json["from_chat"]
        to_user = text_data_json['to_user']

        await self.channel_layer.group_send(self.room_group_name, {"type": "chat.message", "from_chat": from_chat,
                                                                   'to_user': to_user, })

    async def chat_message(self, event):
        from_chat = event["from_chat"]
        to_user = event['to_user']
        await self.send(text_data=json.dumps({"from_chat": from_chat, 'to_user': to_user,
                                              'time': timezone.now().strftime('%H:%M')}))

    async def chat_online(self, event):
        status_online = event['status_online']
        last_online = event['last_online']
        from_user = event['from_user']
        await self.send(text_data=json.dumps({"from_user": from_user, "status_online": status_online,
                                              'last_online': last_online}))

    def change_user_online_status(self, online_status):
        user_profile = Profile.objects.get(user=self.scope['user'])
        user_profile.status_online = online_status
        user_profile.save()

    def check_user_online_status(self):
        user_profile = Profile.objects.get(user=self.scope['user'])
        return user_profile.status_online
