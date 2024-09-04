"""
Views for lobby, public and personal chat rooms.
"""

from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model
from django.http import Http404

from rooms.models import (
    Message,
    PersonalChatRoom,
)

User = get_user_model()


class Index(TemplateView):
    """
    View where are the ways for enter in a public or personal chat.
    """
    template_name = 'chat/index.html'

    def post(self, request):
        """
        Verify if friend exists. If have an existing chat with friend, enter the chat.
        else, raise error 404.
        """
        friend = request.POST.get('friend')

        try:
            other_user = User.objects.get(username=friend)
            chat = PersonalChatRoom.objects.filter(
                participants=request.user
            ).filter(
                participants=other_user
            ).first()

            if chat:
                participants = [p.username for p in chat.participants.all()]
                if not request.user.username in participants:
                    raise Http404()

            if not chat:
                chat = PersonalChatRoom.objects.create()
                chat.participants.add(request.user, other_user)

            return redirect('personal-chat', chat_id=chat.id)

        except User.DoesNotExist:
            return render(request, self.template_name, {'error': 'User does not exist'})


class PublicRoomView(TemplateView):
    """
    View for the public room.
    """
    template_name = 'chat/public-room.html'

    def get_context_data(self, room_name):
        context = {
            'room_name': room_name,
        }
        return context


class PersonalChatView(TemplateView):
    """
    View for personal chat.
    """
    template_name = 'chat/personal-chat.html'

    def dispatch(self, request, *args, **kwargs):
        """
        ]Validate if the user is authenticated and if the user 
        is one of the chat participants.
        """

        if not request.user.is_authenticated:
            raise Http404()

        chat = PersonalChatRoom.objects.get(id=kwargs['chat_id'])
        participants = [p.username for p in chat.participants.all()]

        if not request.user.username in participants:
            raise Http404()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, chat_id, **kwargs):
        """
        Retrieve the chat messages and send the context.
        """
        context = super().get_context_data(**kwargs)

        chat = PersonalChatRoom.objects.get(id=chat_id)
        messages = Message.objects.filter(chat=chat)
        participants = chat.participants.all()

        friend = next((
            p.username for p in participants
            if p.username != self.request.user.username
        )
        )
        context.update({
            'chat': chat,
            'messages': messages,
            'chat_id': chat_id,
            'friend': friend,
        })

        return context
