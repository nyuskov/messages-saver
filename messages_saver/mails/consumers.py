import json

from channels.consumer import AsyncConsumer
from .services import get_messages, get_info, get_progress


class MessageConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        await self.send({"type": "websocket.accept"})

    async def websocket_receive(self, text_data):
        data = json.loads(text_data['text'])
        message = data.get("message")
        if message == "info":
            text = {
                "info": await get_info()
            }
        elif message == "progress":
            text = {
                "progress": await get_progress()
            }
        else:
            text = {
                "messages": await get_messages(
                    data.get("last_message_id", 0))
            }

        await self.send({
            "type": "websocket.send",
            "text": json.dumps(text)
        })

    async def websocket_disconnect(self, event):
        pass
