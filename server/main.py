import os
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from server.config import settings
from server.sync_manager import SyncManager
from server.media_handler import router as media_router
from shared.messages import (
    BaseMessage,
    TimeUpdate,
    Play,
    Pause,
    Seek,
    Load,
    Chat,
    Sync,
)

app = FastAPI()
sync = SyncManager()

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

app.mount("/static", StaticFiles(directory="client/web"), name="static")
app.include_router(media_router)

@app.websocket(settings.ws_path)
async def websocket_endpoint(ws: WebSocket):
    await sync.connect(ws)

    try:
        while True:
            data = await ws.receive_text()
            msg = BaseMessage.parse_raw(data)

            match msg.type:
                case "chat":
                    chat_msg = Chat.parse_raw(data)
                    await sync.broadcast(chat_msg)

                case "sync":
                    sync_msg = Sync.parse_raw(data)
                    await sync.broadcast(sync_msg)

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
        sync.disconnect(ws)

if __name__ == "__main__":
    os.makedirs(settings.media_dir, exist_ok=True)
    uvicorn.run("server.main:app", host=settings.host, port=settings.port, reload=True)
