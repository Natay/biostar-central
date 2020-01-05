import uuid
from django.db import models
#from django.contrib.auth import
from biostar.accounts.models import User
from biostar.utils.markdown import parse
from datetime import datetime
from django.utils.timezone import utc


def now():
    return datetime.utcnow().replace(tzinfo=utc)


def get_uuid(limit=32):
    return str(uuid.uuid4())[:limit]


class ChatRoom(models.Model):

    users = models.ManyToManyField(User)
    creator = models.ForeignKey(User, null=True, related_name='creator', on_delete=models.SET_NULL)
    creation_date = models.DateTimeField(auto_now_add=True)
    lastedit_date = models.DateTimeField(auto_now_add=True)

    name = models.CharField(default="Chat room", max_length=300)
    uid = models.CharField(unique=True, max_length=300)

    def save(self, *args, **kwargs):
        self.uid = self.uid or get_uuid(20)
        self.lastedit_date = self.lastedit_date or now()
        super(ChatRoom, self).save(*args, **kwargs)


class ChatMessage(models.Model):

    # This is the text that the user enters.
    content = models.TextField(default='')

    # This is the  HTML that gets displayed.
    html = models.TextField(default='')
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    lastedit_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.html = self.html or parse(self.content)
        self.lastedit_date = self.lastedit_date or now()
        super(ChatMessage, self).save(*args, **kwargs)


