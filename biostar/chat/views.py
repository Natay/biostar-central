from django.shortcuts import render, redirect, reverse
from django.utils.safestring import mark_safe
from biostar.chat.models import ChatRoom
import json

def index(request):

    user = request.user
    chat_rooms = ChatRoom.objects.filter()
    if user.is_anonymous:
        return redirect(reverse('login'))

    return render(request, 'chat/room_list.html', {})

def room(request, room_name):

    user = request.user
    if user.is_anonymous:
        return redirect(reverse('login'))

    return render(request, 'chat/room_view.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })