# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class GuessWhoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.code = self.scope["url_route"]["kwargs"]["game_code"]
        self.room_group_name = f"guesswho_{self.code}"

        # join group
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

    # receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)

        # send message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game_message",
                "data": data
            }
        )

    # receive from group
    async def game_message(self, event):
        await self.send(text_data=json.dumps(event["data"]))
