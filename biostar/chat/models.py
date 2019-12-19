from django.db import models
#from django.contrib.auth import

class Room:


    users = models.ManyToManyField

    pass


class ChatMessage:

    body = ''
    html = ''

    pass


class Chat:

    message = models.ForeignKey(ChatMessage, on_delete=models.SET_NULL, null=True)

    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    sender = models.ForeignKey


    pass


