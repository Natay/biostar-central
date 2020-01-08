from django.shortcuts import render, redirect, reverse
from django.utils.safestring import mark_safe
from django.conf import settings
from biostar.chat.models import ChatRoom
import channels
import json


def index(request):

    user = request.user
    room_uid = request.GET.get("room_uid", settings.INIT_CHAT)
    if user.is_anonymous:
        return redirect(reverse('login'))
    chat_rooms = user.chatroom_set.order_by('creation_date')

    initial_room = user.chatroom_set.filter(uid=room_uid).first()
    initial_msgs = initial_room.chatmessage_set.order_by('creation_date')

    context = dict(chat_rooms=chat_rooms, initial_room=initial_room, initial_msgs=initial_msgs)

    return render(request, 'chat/room_list.html', context)


def room(request, room_name):

    user = request.user
    if user.is_anonymous:
        return redirect(reverse('login'))

    print(channels.__version__)
    # Filter for the chat rooms this user is in.
    context = dict(room_name_json=mark_safe(json.dumps(room_name)), )
    return render(request, 'chat/room_view.html', context)