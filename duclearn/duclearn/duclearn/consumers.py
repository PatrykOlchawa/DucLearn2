# consumers.py
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger("guesswho")

class GuessWhoConsumer(AsyncWebsocketConsumer):
    # track connected channels and which ones have sent 'ready'
    connected = {}   # { game_code: set(channel_name) }
    ready = {}       # { game_code: set(channel_name) }

    async def connect(self):
        self.game_code = self.scope["url_route"]["kwargs"]["game_code"]
        self.room_group_name = f"guesswho_{self.game_code}"

        # join group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # register connection
        GuessWhoConsumer.connected.setdefault(self.game_code, set()).add(self.channel_name)
        GuessWhoConsumer.ready.setdefault(self.game_code, set())

        logger.info(f"[CONNECT] game={self.game_code} channel={self.channel_name} connected")
        # Optionally notify group that someone connected
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "game_event", "data": {"type": "ws_connect", "channel": self.channel_name}}
        )

    async def disconnect(self, close_code):
        # cleanup
        GuessWhoConsumer.connected.get(self.game_code, set()).discard(self.channel_name)
        GuessWhoConsumer.ready.get(self.game_code, set()).discard(self.channel_name)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f"[DISCONNECT] game={self.game_code} channel={self.channel_name} disconnected")

    async def receive(self, text_data):
        data = json.loads(text_data)
        logger.info(f"[RECEIVE] game={self.game_code} channel={self.channel_name} data={data}")
        msg_type = data.get("type")
        if msg_type == "new_question":
            await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game_event",
                "data": {
                    "type": "new_question",
                    "question": data["question"],
                    "user": data["user"]
                }
            }
            )
            return

        if msg_type == "new_answer":
            await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game_event",
                "data": {
                    "type": "new_answer",
                    "answer": data["answer"],
                    "user": data["user"]
                }
            }
            )
            return
        # handle 'ready' specially
        if msg_type == "ready":
            GuessWhoConsumer.ready.setdefault(self.game_code, set()).add(self.channel_name)
            logger.info(f"[READY] game={self.game_code} ready_count={len(GuessWhoConsumer.ready[self.game_code])} connected_count={len(GuessWhoConsumer.connected.get(self.game_code, set()))}")

            # Check both players are connected and both sent ready
            if len(GuessWhoConsumer.ready[self.game_code]) >= 2 and len(GuessWhoConsumer.connected.get(self.game_code, set())) >= 2:
                logger.info(f"[STARTING] game={self.game_code} broadcasting start_game")
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "game_event", "data": {"type": "start_game"}}
                )
            return
        
        # otherwise broadcast to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "game_event", "data": data}
        )

    # called when group_send includes "type": "game_event"
    async def game_event(self, event):
        logger.info(f"[GAME_EVENT -> SEND] game={self.game_code} event={event['data']}")
        await self.send(text_data=json.dumps(event["data"]))
