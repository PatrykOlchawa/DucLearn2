from django.urls import path
from . import consumers

websocket_urlpatterns = [
            path("ws/guess_who/<str:game_code>/", consumers.GuessWhoConsumer.as_asgi()),
        ]
