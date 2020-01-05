from functools import wraps, partial
import logging
from django.template import loader
from django.http import JsonResponse
from django.utils.decorators import available_attrs
from django.utils.safestring import mark_safe
from biostar.chat.models import ChatRoom,ChatMessage


def ajax_msg(msg, status, **kwargs):
    payload = dict(status=status, msg=msg)
    payload.update(kwargs)
    return JsonResponse(payload)


logger = logging.getLogger("biostar")
ajax_success = partial(ajax_msg, status='success')
ajax_error = partial(ajax_msg, status='error')

MIN_TITLE_CHARS = 10
MAX_TITLE_CHARS = 180

MAX_TAGS = 5


class ajax_error_wrapper:
    """
    Used as decorator to trap/display  errors in the ajax calls
    """

    def __init__(self, method, login_required=True):
        self.method = method
        self.login_required = login_required

    def __call__(self, func, *args, **kwargs):

        @wraps(func, assigned=available_attrs(func))
        def _ajax_view(request, *args, **kwargs):

            if request.method != self.method:
                return ajax_error(f'{self.method} method must be used.')

            if not request.user.is_authenticated and self.login_required:
                return ajax_error('You must be logged in.')

            return func(request, *args, **kwargs)

        return _ajax_view


@ajax_error_wrapper(method="GET", login_required=True)
def ajax_create_room(request):

    name = request.GET.get('name', "Chat room")
    user = request.user

    chat_room = ChatRoom.objects.create(name=name)

    chat_room.users.add(user)
    chat_room.save()

    return ajax_success(msg="success", )


@ajax_error_wrapper(method="GET", login_required=True)
def ajax_room_list(request):

    # Get the user from the
    user = request.user

    # Filter for the chat rooms this user is in.
    chat_rooms = user.chatroom_set.all()#ChatRoom.objects.filter(users__contains=user)

    # Render the template
    tmpl = loader.get_template("chat/room_list.html")
    context = dict(chat_rooms=chat_rooms)

    rooms_html = tmpl.render(context)

    return ajax_success(msg="success", html=rooms_html)


@ajax_error_wrapper(method="GET", login_required=True)
def ajax_room_view(request, room_uid):

    room = ChatRoom.objects.filter(uid=room_uid).first()
    if room:
        messages = room.chatmessage_set.order_by('-creation_date')
    else:
        messages = []

    tmpl = loader.get_template("chat/room_view.html")
    context = dict(messages=messages, room_name_json=mark_safe(room_uid))

    messages_html = tmpl.render(context)

    return ajax_success(msg="success", html=messages_html)


