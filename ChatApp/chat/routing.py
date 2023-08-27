# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/group/(?P<room_name>\w+)/$", consumers.GroupConsumer.as_asgi()),
    re_path(r"ws/general/", consumers.GeneralConsumer.as_asgi()),
]