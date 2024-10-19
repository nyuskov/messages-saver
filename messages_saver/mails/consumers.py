import json

from channels.consumer import AsyncConsumer
from .services import (
    get_messages, download_messages, get_progress, get_auth_info)


class MessageConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        await self.send({"type": "websocket.accept"})

    async def websocket_receive(self, text_data):
        message = json.loads(text_data['text']).get(
            "message")
        text = ""
        if message == "download_messages":
            text = {
                "info": await download_messages()
            }
        elif message == "get_messages":
            text = {
                "messages": await get_messages()
            }
        elif message == "get_auth_info":
            text = {
                "auth_info": await get_auth_info()
            }
        elif message == "progress":
            text = {
                "progress": await get_progress()
            }

        await self.send({
            "type": "websocket.send",
            "text": json.dumps(text)
        })

    async def websocket_disconnect(self, event):
        pass
