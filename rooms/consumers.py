"""
Consumers for public chat and personal chat.
"""

from datetime import datetime

import json

from channels.generic.websocket import AsyncWebsocketConsumer

from rooms.models import (
    PersonalChatRoom,
    Message
)


class PublicRoomConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling chat functionality in a group chat setting.
    """
    users_count = {}

    async def connect(self):
        """
        Handles a new WebSocket connection to the chat.Initializes the 
        room name and group. Increments the user count, and broadcasts 
        the updated user count to the group.
        """
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        print(self.channel_layer)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        if self.room_group_name not in self.users_count:
            self.users_count[self.room_group_name] = 0
        self.users_count[self.room_group_name] += 1

        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_count',
                'count': self.users_count[self.room_group_name]
            }
        )

    async def disconnect(self, code):
        """
        Handles the WebSocket disconnection. Decrements the 
        user count, and broadcasts the updated user count 
        to the group.
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        if self.room_group_name in self.users_count:
            self.users_count[self.room_group_name] -= 1

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_count',
                'count': self.users_count[self.room_group_name]
            }
        )

    async def receive(self, text_data):
        """
        Handles incoming messages sent by the WebSocket client.
        Parses the incoming JSON message and broadcasts it to the group.
        """
        data = json.loads(text_data)
        message = data['message']
        username = data['username']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    async def chat_message(self, event):
        """
        Receives messages sent to the group and sends them 
        to the WebSocket client.
        """
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    async def user_count(self, event):
        """
        Receives user count updates and sends them to 
        the WebSocket client.
        """
        count = event['count']

        await self.send(text_data=json.dumps({
            'user_count': count
        }))


class PersonalChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling chat functionality in a 
    personal chat.
    """

    async def connect(self):
        """
        Handles a new WebSocket connection to the personal chat.
        Initializes the chat ID and group, adds the connection to the group.
        """
        self.user = self.scope['user']
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'

        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, code):
        """
        Handles the WebSocket disconnection.
        """
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        """
        Handles incoming messages sent by the WebSocket client.
        Parses the incoming JSON message, saves it to the database, 
        and broadcasts it to the group.
        """
        data = json.loads(text_data)
        message = data['message']
        timestamp = datetime.fromtimestamp(data['timestamp'] / 1000)

        chat = await PersonalChatRoom.objects.aget(
            id=self.chat_id
        )
        await Message.objects.acreate(
            chat=chat,
            sender=self.user,
            content=message,
            timestamp=timestamp,
        )

        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username,
                'timestamp': timestamp.strftime(
                    '%I:%M %p').replace('AM', 'a.m').replace('PM', 'p.m.'),
            })

    async def chat_message(self, event):
        """
        Receives messages sent to the personal chat group and sends 
        them to the WebSocket client.
        """
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'timestamp': timestamp,
        }))
