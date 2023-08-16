from django.urls import path, include
from .views import *
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', MainMenu.as_view(), name='home'),
    path("chat/<int:room_name>", ChatPage.as_view(), name="chat-page"),
    path('search/<str:search_name>', SearchUsers.as_view(), name='search_users'),
    path('newchat/<int:id_user>', new_chat, name='new_chat'),
    path('logout/', logout_user, name='logout'),

    # login-section
    path("login/", LoginUser.as_view(), name="login"),
    path("registration/", RegisterUser.as_view(), name="register"),
]