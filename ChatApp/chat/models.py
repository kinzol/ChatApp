from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Chat(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='user1')
    user2 = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='user2')
    time_create = models.DateTimeField(auto_now_add=True)

class Messages(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    content = models.TextField(max_length=255)
    time_create = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=True)
    chat_id = models.IntegerField()
    #chat_id = models.ForeignKey(Chat, on_delete=models.SET_NULL, blank=True, null=True)