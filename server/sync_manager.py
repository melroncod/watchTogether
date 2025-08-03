import json
from typing import Set
from fastapi import WebSocket
from shared.messages import BaseMessage
from server.utils import get_logger

logger = get_logger("sync_manager")

class SyncManager:
    def __init__(self):
        self.connections: Set[WebSocket] = set()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.add(ws)
        logger.info(f"Client connected: {ws.client}")

    def disconnect(self, ws: WebSocket):
        self.connections.discard(ws)
        logger.info(f"Client disconnected: {ws.client}")

    async def broadcast(self, message: BaseMessage):
        data = message.json()
        logger.debug(f"Broadcasting: {data}")
        to_remove = []
        for conn in self.connections:
            try:
                await conn.send_text(data)
            except Exception:
                to_remove.append(conn)
        for conn in to_remove:
            self.disconnect(conn)
