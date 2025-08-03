import asyncio
import json
import sys
import httpx
import websockets
from client.cli.config import settings
from shared.messages import TimeUpdate, Play, Pause, Seek

async def interactive():
    uri = settings.ws_host
    async with websockets.connect(uri) as ws:
        print(f"Connected to {uri}")
        async def producer():
            while True:
                cmd = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                parts = cmd.strip().split()
                if not parts:
                    continue
                match parts[0]:
                    case "load":
                        target = parts[1]
                        if target.startswith("http"):
                            print("Loading URL:", target)
                        else:
                            # проверка существования файла
                            resp = httpx.head(f"{settings.http_host}{target}")
                            resp.raise_for_status()
                            print("Loading file:", target)
                    case "play":
                        await ws.send(json.dumps({"type":"play"}))
                    case "pause":
                        await ws.send(json.dumps({"type":"pause"}))
                    case "seek":
                        t = float(parts[1])
                        await ws.send(json.dumps({"type":"seek","time":t}))
                    case "exit":
                        break

        async def consumer():
            async for message in ws:
                msg = json.loads(message)
                print("←", msg)

        await asyncio.gather(producer(), consumer())

if __name__ == "__main__":
    try:
        asyncio.run(interactive())
    except KeyboardInterrupt:
        print("Exit")
