"""
Models for personal chat and messages.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class PersonalChatRoom(models.Model):
    """
    Set a room for the participants.
    """
    participants = models.ManyToManyField(
        User,
    )


class Message(models.Model):
    """
    Create a message with a user, chat room and timestamp.
    """
    chat = models.ForeignKey(
        PersonalChatRoom,
        on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField()

    class Meta:
        ordering = ('-timestamp',)
