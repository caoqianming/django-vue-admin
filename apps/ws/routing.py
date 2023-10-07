from django.urls import path
from apps.ws.consumers import MyConsumer, RoomConsumer

WS_BASE_URL = 'ws/'

websocket_urlpatterns = [
    path(f'{WS_BASE_URL}my/', MyConsumer.as_asgi()),
    path(WS_BASE_URL + '<str:room_name>/', RoomConsumer.as_asgi()),
]