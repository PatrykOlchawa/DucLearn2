# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GuessWhoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_code = self.scope["url_route"]["kwargs"]["game_code"]
        self.room_group_name = f"guesswho_{self.game_code}"

        # join WebSocket group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # message received from WebSocket (client)
    async def receive(self, text_data):
        data = json.loads(text_data)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game_event",
                "data": data
            }
        )

    # message sent to all clients in the group
    async def game_event(self, event):
        await self.send(text_data=json.dumps(event["data"]))
