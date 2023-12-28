from django.urls import path
from .views import *

urlpatterns = [
    path('', MainMenu.as_view(), name='home'),
    path("chat/<int:room_name>", ChatPage.as_view(), name="chat-page"),
    path('search/<str:search_name>', SearchUsers.as_view(), name='search_users'),
    path('newchat/<int:id_user>', new_chat, name='new_chat'),
    path('settings/', Settings.as_view(), name='settings'),
    path('user/<str:username>', UserProfile.as_view(), name='user_profile'),
    path('delete_message/<int:message_id>/<int:from_chat>/', delete_message, name='delete-message'),

    # group
    path('create-group', CreateGroup.as_view(), name='create_group'),
    path("group/<int:room_name>", GroupPage.as_view(), name="group-page"),
    path('group-info/<int:room_name>', GroupInfo.as_view(), name='group-info'),
    path('group-give-admin/<int:user>/<int:from_group>', group_give_admin, name='group_give_admin'),
    path('group-remove-admin/<int:user>/<int:from_group>', group_remove_admin, name='group_remove_admin'),
    path('group-kick/<int:user>/<int:from_group>', group_kick, name='group_kick'),
    path('group-add/<int:from_group>', GroupAdd.as_view(), name='group_add'),

    # auth
    path('logout/', logout_user, name='logout'),
    path("login/", LoginUser.as_view(), name="login"),
    path("registration/", RegisterUser.as_view(), name="register"),
]
