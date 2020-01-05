from django.urls import re_path, path
from biostar.chat import consumers, views, ajax


urlpatterns = [
    path('', views.index, name='ajax_room_list'),
    path('<str:room_name>/', views.room, name='room'),
    path('ajax/<str:room_uid>/', ajax.ajax_room_view, name='ajax_room_view'),
    # path('ajax/form/', ajax.inplace_form, name='inplace_form'),
    # path('ajax/search/', ajax.ajax_search, name='ajax_search'),

]

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>[-\w]+)/$', consumers.SyncChatConsumer),
]
