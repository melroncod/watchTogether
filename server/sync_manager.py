import os
import json
from typing import Set
from fastapi import WebSocket
from shared.messages import BaseMessage, Chat
from server.config import settings
from server.utils import get_logger

logger = get_logger("sync_manager")

class SyncManager:
    def __init__(self):
        self.connections: Set[WebSocket] = set()
        # Папка для хранения истории чата рядом с media
        base_dir = os.path.dirname(settings.media_dir)
        history_dir = os.path.join(base_dir, "chathistory")
        os.makedirs(history_dir, exist_ok=True)
        self.history_file = os.path.join(history_dir, "chat_history.json")
        self.chat_history: list[dict] = []
        self._load_history()

    def _load_history(self):
        if not os.path.exists(self.history_file):
            return
        try:
            # если файл пустой или некорректный, JSONDecodeError
            with open(self.history_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    self.chat_history = json.loads(content)
                    logger.info("Loaded chat history (%d messages)", len(self.chat_history))
                else:
                    self.chat_history = []
        except json.JSONDecodeError:
            logger.error("Failed to parse chat history JSON, starting fresh")
            self.chat_history = []
        except Exception as e:
            logger.error("Failed to load chat history: %s", e)
            self.chat_history = []

    def _save_history(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
            logger.debug("Chat history saved")
        except Exception as e:
            logger.error("Failed to save chat history: %s", e)

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.connections.add(ws)
        logger.info("Client connected: %s", ws.client)
        # Отправляем всю историю новому клиенту
        for msg in self.chat_history:
            try:
                await ws.send_text(json.dumps(msg))
            except Exception:
                pass

    def disconnect(self, ws: WebSocket):
        self.connections.discard(ws)
        logger.info("Client disconnected: %s", ws.client)

    async def broadcast(self, message: BaseMessage):
        data = message.json()
        logger.debug("Broadcasting: %s", data)
        if isinstance(message, Chat):
            self.chat_history.append(message.dict())
            self._save_history()

        to_remove = []
        for conn in self.connections:
            try:
                await conn.send_text(data)
            except Exception:
                to_remove.append(conn)
        for conn in to_remove:
            self.disconnect(conn)
