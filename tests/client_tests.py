import pytest
import asyncio
import websockets
import json
from client.cli.config import settings

@pytest.mark.asyncio
async def test_cli_ws_echo(tmp_path, monkeypatch):
    # Поднимаем echo-сервер
    async def echo(ws):
        async for msg in ws:
            await ws.send(msg)

    server = await websockets.serve(echo, "localhost", 8765)
    monkeypatch.setenv("SYNC_WS_HOST", "ws://localhost:8765")
    uri = settings.ws_host

    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"type":"pause"}))
        resp = await ws.recv()
        assert json.loads(resp)["type"] == "pause"

    server.close()
    await server.wait_closed()
