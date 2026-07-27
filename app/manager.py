from fastapi import WebSocket
from datetime import datetime


class ConnectionManager:

    def __init__(self):
        self.connections = {}
        self.online_users = set()

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()

        self.connections[username] = websocket
        self.online_users.add(username)

        await self.broadcast_online_users()

    async def disconnect(self, username: str):

        if username in self.connections:
            del self.connections[username]

        if username in self.online_users:
            self.online_users.remove(username)

        await self.broadcast_online_users()

    async def broadcast_online_users(self):

        data = {
            "type": "online",
            "users": list(self.online_users)
        }

        for ws in self.connections.values():
            await ws.send_json(data)

    async def send_private_message(
        self,
        sender,
        receiver,
        message
    ):

        if receiver in self.connections:

            await self.connections[receiver].send_json({
                "type": "message",
                "from": sender,
                "message": message,
                "time": datetime.now().strftime("%I:%M %p")
            })

        if sender in self.connections:

            await self.connections[sender].send_json({
                "type": "delivered"
            })

    async def send_typing(
        self,
        sender,
        receiver
    ):

        if receiver in self.connections:

            await self.connections[receiver].send_json({
                "type": "typing",
                "from": sender
            })

    async def send_seen(
        self,
        sender,
        receiver
    ):

        if sender in self.connections:

            await self.connections[sender].send_json({
                "type": "seen"
            })


manager = ConnectionManager()