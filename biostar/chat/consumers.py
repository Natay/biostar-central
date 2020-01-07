import json
from datetime import datetime

from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async
from biostar.chat.models import ChatRoom, ChatMessage
from django.conf import settings
from django.utils.timezone import utc


def now():
    return datetime.utcnow().replace(tzinfo=utc)


class SyncChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']

        # Check to see if this is a chat this user can see.
        #user = self.scope['user']

        # Check to see if this users is is included in this chat
        #chat_room = user.chatroom_set.filter(uid=self.room_name)

        # Disconnect if it does not.
        #if not chat_room.exists():
        #    self.disconnect(404)
        #    return

        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        content = message.split('|/')[0]
        user = self.scope['user']
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )
        # Send message to room group
        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_group_name,
        #     {
        #         'type': 'chat_user',
        #         'user': user
        #     }
        # )
        # Get the current chat room
        #try:
        #room = ChatRoom.objects.filter(uid=self.room_name).first()
        #ChatMessage.objects.create(content=content, author=user, room=room)
        # Create the message

        #print(text_data, user, self.room_name, msg)

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

    # Receive message from room group
    # def chat_user(self, event):
    #     user = self.scope['user']#event['message']
    #
    #     # Send message to WebSocket
    #     self.send(text_data=json.dumps({
    #         'user': user
    #     }))

class AsyncChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


def get_consumer():

    if settings.ASYNC_CHAT:

        return AsyncChatConsumer

    return SyncChatConsumer
