import os
import json
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from server.config import settings
from server.sync_manager import SyncManager
from server.media_handler import router as media_router
from shared.messages import (
    BaseMessage, TimeUpdate, Play, Pause, Seek, Load, Chat, ClearChat, ChatHistory
)

HISTORY_PATH = os.path.join(settings.media_dir, "chat_history.json")

app = FastAPI()
sync = SyncManager()

# загрузка истории при старте
if os.path.exists(HISTORY_PATH):
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        sync.chat_history = [Chat(**m) for m in json.load(f)]
else:
    sync.chat_history = []

def save_history():
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump([m.dict() for m in sync.chat_history], f, ensure_ascii=False, indent=2)

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

app.mount("/static", StaticFiles(directory="client/web"), name="static")
app.include_router(media_router)

@app.websocket(settings.ws_path)
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    sync.connections.add(ws)
    # сразу шлём всю историю новому клиенту
    for msg in sync.chat_history:
        await ws.send_text(msg.json())

    try:
        while True:
            data = await ws.receive_text()
            msg = BaseMessage.parse_raw(data)
            match msg.type:
                case "chat":
                    chat_msg = Chat.parse_raw(data)
                    sync.chat_history.append(chat_msg)
                    save_history()
                    await sync.broadcast(chat_msg)
                case "clear_chat":
                    # очистка истории
                    sync.chat_history.clear()
                    save_history()
                    clear_msg = ClearChat()
                    await sync.broadcast(clear_msg)
                case "time_update":
                    await sync.broadcast(TimeUpdate.parse_raw(data))
                case "play":
                    await sync.broadcast(Play())
                case "pause":
                    await sync.broadcast(Pause())
                case "seek":
                    await sync.broadcast(Seek.parse_raw(data))
                case "load":
                    await sync.broadcast(Load.parse_raw(data))
                case _:
                    pass
    except WebSocketDisconnect:
        sync.connections.discard(ws)

if __name__ == "__main__":
    os.makedirs(settings.media_dir, exist_ok=True)
    uvicorn.run("server.main:app", host=settings.host, port=settings.port, reload=True)
