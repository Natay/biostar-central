from django.db import models
#from django.contrib.auth import
from biostar.accounts.models import User


class ChatThread(models.Model):

    users = models.ManyToManyField(User)
    name = models.CharField(default="Chat room", max_length=300)
    uid = models.CharField(unique=True, max_length=300)


class ChatMessage(models.Model):

    # This is the text that the user enters.
    content = models.TextField(default='')

    # This is the  HTML that gets displayed.
    html = models.TextField(default='')
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)


