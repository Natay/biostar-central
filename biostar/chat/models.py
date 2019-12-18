from django.db import models
#from django.contrib.auth import

class Room:


    users = models.ManyToManyField

    pass


class Chat:
    pass


class ChatMessage:

    body = ''
    date = ''
    deleted = False


    pass