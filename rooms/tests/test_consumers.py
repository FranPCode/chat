"""
Test for websocket consumers.
"""
from asgiref.sync import SyncToAsync

import time

import json

from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from channels.db import database_sync_to_async

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import path

from rooms.consumers import (
    PersonalChatConsumer,
    PublicRoomConsumer,
)
from rooms.models import (
    PersonalChatRoom,
    Message
)

User = get_user_model()


class PublicRoomTest(TestCase):
    """
    Test the behavior of the consumer for the public room.
    """

    async def _set_communicator(self):
        """
        Configure the app for routing.
        """
        application = URLRouter([
            path("ws/chat/<str:room_name>/",
                 PublicRoomConsumer.as_asgi()),
        ])
        communicator = WebsocketCommunicator(application, "/ws/chat/test/")
        connected, subprotocol = await communicator.connect()

        return communicator, connected, subprotocol

    async def test_connection_and_user_count(self):
        """
        Test the connection and the user count increment when
        new user connects to room.
        """
        communicator, connected, subprotocol = await self._set_communicator()
        self.assertTrue(connected)
        response = await communicator.receive_json_from()
        self.assertEqual(response['user_count'], 1)

        communicator2, connected2, subprotocol2 = await self._set_communicator()
        self.assertTrue(connected2)
        response2 = await communicator.receive_json_from()
        self.assertEqual(response2['user_count'], 2)

        await communicator.disconnect()
        await communicator2.disconnect()

    async def test_receive_message(self):
        """
        Test message broadcasting to all users.
        """
        data = {
            'message': 'testing',
            'username': 'testingusername'
        }
        communicator, connected, subprotocol = await self._set_communicator()
        communicator2, connected2, subprotocol2 = await self._set_communicator()

        await communicator.send_json_to(data)
        await communicator2.receive_from()

        response = await communicator2.receive_json_from()
        self.assertEqual(response, data)

        await communicator.receive_json_from()
        await communicator.receive_json_from()
        response2 = await communicator.receive_json_from()
        self.assertEqual(response2, data)

    async def test_disconnect_and_user_count(self):
        """
        Test disconnection and user count decrease.
        """
        communicator, connected, subprotocol = await self._set_communicator()
        communicator2, connected2, subprotocol2 = await self._set_communicator()
        communicator3, connected3, subprotocol3 = await self._set_communicator()

        response = await communicator3.receive_json_from()
        self.assertEqual(response['user_count'], 3)

        await communicator.disconnect()

        response = await communicator3.receive_json_from()
        self.assertEqual(response['user_count'], 2)

        await communicator2.disconnect()
        await communicator3.disconnect()

    async def test_invalid_message(self):
        """
        Test handling of an invalid message.
        """
        communicator, connected, subprotocol = await self._set_communicator()
        await communicator.receive_json_from()
        await communicator.send_json_to({'message': 'invalid test'})

        response = await communicator.receive_json_from()
        self.assertEqual(
            response, {'error': 'Invalid message format or missing data'})

        await communicator.disconnect()


class PersonalChatTest(TestCase):
    """
    Test the behavior of the consumer for the personal chat.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser1',
            email='user1@test.com',
            password='testpassword1'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='user2@test.com',
            password='testpassword2'
        )
        self.chat = PersonalChatRoom.objects.create()
        self.chat.participants.add(self.user)
        self.chat.participants.add(self.user2)

    async def _set_communicator(self, user, chat_id):
        """
        Configure the app for routing, set user to scope and chat id.
        """
        application = URLRouter([
            path("ws/chat/<int:chat_id>",
                 PersonalChatConsumer.as_asgi()),
        ])
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{chat_id}"
        )
        communicator.scope['user'] = user
        connected, _ = await communicator.connect()

        return communicator, connected

    async def test_connection(self):
        """
        Test the connection with auth user.
        """
        communicator, connected = await self._set_communicator(
            self.user, self.chat.id
        )
        communicator2, connected2 = await self._set_communicator(
            self.user2, self.chat.id
        )

        self.assertTrue(connected)
        self.assertTrue(connected2)

        await communicator.disconnect()
        await communicator2.disconnect()

    async def test_send_message(self):
        """
        Test send and create a message.
        """
        communicator, connected = await self._set_communicator(
            self.user, self.chat.id
        )
        communicator2, connected2 = await self._set_communicator(
            self.user2, self.chat.id
        )
        payload = {
            'message': 'test message',
            'timestamp': time.time(),
        }
        await communicator.send_json_to(payload)

        response = await communicator2.receive_json_from(10)
        response2 = await communicator.receive_json_from(10)

        self.assertEqual(payload['message'], response['message'])
        self.assertEqual(payload['message'], response2['message'])
        self.assertEqual(self.user.username, response2['sender'])
        self.assertIn('timestamp', response)

        message = await Message.objects.aget(sender=self.user)
        self.assertTrue(message)

        await communicator.disconnect()
        await communicator2.disconnect()
