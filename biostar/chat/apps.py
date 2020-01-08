import logging
from django.db.models.signals import post_migrate
from django.conf import settings
from django.contrib.auth import get_user_model
from django.apps import AppConfig

logger = logging.getLogger('engine')


class ChatConfig(AppConfig):
    name = 'biostar.chat'

    def ready(self):
        post_migrate.connect(init_chat, sender=self)


def init_chat(sender, **kwargs):

    from biostar.chat.models import ChatRoom, ChatMessage
    User = get_user_model()
    user = User.objects.filter(is_superuser=True).first()
    uid = settings.INIT_CHAT
    # Create the chat room if it does not exist.
    room = ChatRoom.objects.filter(uid=uid).first()

    if room:
        if settings.DEBUG:
            ChatRoom.objects.filter(uid=uid).delete()

    room = ChatRoom.objects.create(name="Hello from biostars!", uid=uid, creator=user)
    # Create the chat message
    ChatMessage.objects.create(content="Hello! Welcome to the biostar chat. Feel free to interact.",
                               author=user, room=room)
    # Add all users to this room (for now)
    room.users.add(*User.objects.all())
    room.save()
