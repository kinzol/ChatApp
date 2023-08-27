from datetime import datetime

from django.db.models import Q
from django.utils import timezone

from .models import *

class DataMixin:

    def get_user_context(self, **kwargs):
        context = kwargs
        chats = Chat.objects.filter(participants=self.request.user)
        groups = Group.objects.filter(participants=self.request.user)
        list_chats_and_groups = []
        last_messages = {}

        for chat in chats:
            try:
                message = Messages.objects.filter(chat_id=chat.pk).order_by('-id')[:1][0]
                last_messages[chat.pk] = message.time_create
                count_read = Messages.objects.filter(~Q(user=self.request.user.id), chat_id=chat.pk, read=False, )
                chat_users = chat.participants.all()

                if self.request.user == chat_users[0]:
                    user_me, user_mate = chat_users[0], chat_users[1]
                else:
                    user_me, user_mate = chat_users[1], chat_users[0]


                list_chats_and_groups.append({'chat': chat, 'message': message, 'count_read': len(count_read),
                                              'mate': user_mate, 'me': user_me, 'type': 'chat'})
            except Exception:
                last_messages[chat.pk] = timezone.now()
                chat_users = chat.participants.all()
                if self.request.user == chat_users[0]:
                    user_me, user_mate = chat_users[0], chat_users[1]
                else:
                    user_me, user_mate = chat_users[1], chat_users[0]
                list_chats_and_groups.append({'chat': chat, 'message': [], 'count_read': 0,
                                              'mate': user_mate, 'me': user_me, 'type': 'chat'})

        for group in groups:
            try:
                message = GroupMessages.objects.filter(chat_id=group.pk).order_by('-id')[:1][0]
                last_messages[group.pk] = message.time_create
                list_chats_and_groups.append({'chat': group, 'message': message, 'count_read': 0, 'type': 'group'})
            except Exception:
                last_messages[group.pk] = timezone.now()
                list_chats_and_groups.append({'chat': group, 'message': [], 'count_read': 0, 'type': 'group'})

        # Объединение списков чатов и групп
        combined_list = list_chats_and_groups
        sorted_list = sorted(combined_list, key=lambda x: last_messages.get(x['chat'].pk), reverse=True)

        context['chats'] = sorted_list
        return context