from channels.consumer import AsyncConsumer
from .services import get_messages


class MessageConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        await self.send({"type": "websocket.accept"})

    async def websocket_receive(self, text_data):
        await get_messages()
        await self.send({
            "type": "websocket.send",
            "text": "Hello from Django socket"
        })

    async def websocket_disconnect(self, event):
        pass
