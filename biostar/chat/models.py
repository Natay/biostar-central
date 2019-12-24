from django.db import models
#from django.contrib.auth import
from biostar.accounts.models import User

class Room(models.Model):

    users = models.ManyToManyField(User)

    pass


class ChatMessage(models.Model):

    # This is the text that the user enters.
    content = models.TextField(default='')

    # This is the  HTML that gets displayed.
    html = models.TextField(default='')

    pass


class Chat(models.Model):

    message = models.ForeignKey(ChatMessage, on_delete=models.SET_NULL, null=True)

    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


