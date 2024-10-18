import json

from channels.consumer import AsyncConsumer
from .services import get_messages, get_info, get_progress


class MessageConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        await self.send({"type": "websocket.accept"})

    async def websocket_receive(self, text_data):
        message = json.loads(text_data['text']).get("message")
        if message == "info":
            text = await get_info()
        elif message == "progress":
            text = await get_progress()
        else:
            text = await get_messages()

        await self.send({
            "type": "websocket.send",
            "text": text
        })

    async def websocket_disconnect(self, event):
        pass
