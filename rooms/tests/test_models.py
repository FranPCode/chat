"""
Tests for room models.
"""
from django.utils import timezone

from django.test import TestCase
from django.contrib.auth import get_user_model

from rooms.models import (
    PersonalChatRoom,
    Message,
)

User = get_user_model()


class PersonalChatModelTest(TestCase):
    """
    Tests for personal chat.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser1',
            email='user1@test.com',
            password='user1password'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='user2@gmail.com',
            password='user2password'
        )

    def test_create_and_add_users(self):
        """
        test creating a personal chat room and adding users.
        """
        chat = PersonalChatRoom.objects.create()

        chat.participants.add(self.user, self.user2)
        participants = [p.username for p in chat.participants.all()]

        self.assertIn(self.user.username, participants)
        self.assertIn(self.user2.username, participants)


class MessageModelTest(TestCase):
    """
    Tests for message model.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser1',
            email='user1@test.com',
            password='user1password'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='user2@gmail.com',
            password='user2password'
        )


class MessageModelTest(TestCase):
    """
    Tests for message model.
    """

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='password123'
        )
        self.chat = PersonalChatRoom.objects.create()
        self.chat.participants.add(self.user1, self.user2)

    def test_create_message(self):
        """
        Test that a message can be created with a valid user, chat, and timestamp.
        """
        message = Message.objects.create(
            chat=self.chat,
            sender=self.user1,
            content='Hello, this is a test message.',
            timestamp=timezone.now()  # Asegúrate de que timezone.now() es un objeto datetime
        )

        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.chat, self.chat)
        self.assertEqual(message.content, 'Hello, this is a test message.')
        self.assertTrue(message.timestamp)

    def test_message_ordering(self):
        """
        Test that messages are ordered by timestamp in descending order.
        """
        message1 = Message.objects.create(
            chat=self.chat,
            sender=self.user1,
            content='First message',
            timestamp=timezone.now()
        )

        message2 = Message.objects.create(
            chat=self.chat,
            sender=self.user2,
            content='Second message',
            timestamp=timezone.now() + timezone.timedelta(seconds=5)
        )

        messages = Message.objects.all()
        self.assertEqual(messages.first(), message2)
        self.assertEqual(messages.last(), message1)
