from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.manager import manager
from app.database import SessionLocal
from app.models import Message

router = APIRouter()


@router.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):

    await manager.connect(username, websocket)

    try:
        while True:

            data = await websocket.receive_json()
            msg_type = data.get("type")

            # ---------------- Message ----------------
            if msg_type == "message":

                db = SessionLocal()

                new_message = Message(
                    sender=username,
                    receiver=data["to"],
                    message=data["message"],
                    status="sent"
                )

                db.add(new_message)
                db.commit()

                await manager.send_private_message(
                    sender=username,
                    receiver=data["to"],
                    message=data["message"]
                )

                new_message.status = "delivered"
                db.commit()

                db.close()

            # ---------------- Typing ----------------
            elif msg_type == "typing":

                await manager.send_typing(
                    sender=username,
                    receiver=data["to"]
                )

            # ---------------- Seen ----------------
            elif msg_type == "seen":

                await manager.send_seen(
                    sender=data["to"],
                    receiver=username
                )

            # ---------------- Last Seen ----------------
            elif msg_type == "last_seen":

                await manager.send_last_seen(
                    requester=username,
                    target=data["to"]
                )

    except WebSocketDisconnect:

        await manager.disconnect(username)