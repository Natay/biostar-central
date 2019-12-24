from django.urls import re_path, path
from biostar.chat import consumers, views


urlpatterns = [
    path('', views.index, name='index'),
    path('<str:room_name>/', views.room, name='room'),
]


websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.SyncChatConsumer),
]
