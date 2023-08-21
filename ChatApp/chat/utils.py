from django.db.models import Q

from .models import *

class DataMixin:

    def get_user_context(self, **kwargs):
        context = kwargs
        chats = Chat.objects.filter(participants=self.request.user)
        list_chats = []

        for chat in chats:
            try:
                message = Messages.objects.filter(chat_id=chat.pk).order_by('-id')[:1][0]
                count_read = Messages.objects.filter(~Q(user=self.request.user.id), chat_id=chat.pk, read=False,)
                chat_users = chat.participants.all()
                user_mate = chat_users[0] if self.request.user == chat_users[0] else chat_users[1]
                user_me = chat_users[0] if self.request.user != chat_users[0] else chat_users[1]

                list_chats.append([chat, message, len(count_read), user_mate, user_me])
            except Exception:
                chat_users = chat.participants.all()
                user_mate = chat_users[0] if self.request.user == chat_users[0] else chat_users[1]
                user_me = chat_users[0] if self.request.user != chat_users[0] else chat_users[1]
                list_chats.append([chat, [], 0, user_mate, user_me])

        context['chats'] = list_chats
        return context