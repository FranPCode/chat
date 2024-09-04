"""
Routes for websocket connection.
"""

from django.urls import re_path

from rooms import consumers

websocket_urlpatterns = [
    re_path(
        r'ws/chat/(?P<chat_id>\d+)/$',
        consumers.PersonalChatConsumer.as_asgi()
    ),
    re_path(
        r"ws/chat/(?P<room_name>\w+)/$",
        consumers.PublicRoomConsumer.as_asgi()
    ),
]
