"""
Urls for public chat room and personal chat room.
"""
from django.urls import path

from rooms.views import (
    Index,
    PublicRoomView,
    PersonalChatView,
)

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('chat/<int:chat_id>/', PersonalChatView.as_view(), name='personal-chat'),
    path('chat/<str:room_name>/', PublicRoomView.as_view(), name='room'),
]
