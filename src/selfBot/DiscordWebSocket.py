import threading
import typing

import websockets
import zlib
import json
import asyncio

from src.BLogger import BLogger

ZLIB_SUFFIX = b"\x00\x00\xff\xff"

class DiscordWebSocket:
    def __init__(self, token:str):
        self._token = token
        self._decompressor = zlib.decompressobj()
        self._stop = False
        self._logger:BLogger = BLogger(token)
    async def _heartbeat(self, ws, interval):
        while True:
            await asyncio.sleep(interval / 1000)
            await ws.send(json.dumps({"op": 1, "d": None}))
    async def start(self, ready:typing.Callable, readyArgs:tuple):
        async with websockets.connect("wss://gateway.discord.gg/?encoding=json&v=9&compress=zlib-stream") as ws:
            buffer = b""
            while True:
                if self._stop:
                    return
                chunk = await ws.recv()
                if isinstance(chunk, str):
                    continue
                buffer += chunk
                if ZLIB_SUFFIX in buffer:
                    try:
                        msg = self._decompressor.decompress(buffer)
                        buffer = b""
                        data = json.loads(msg)
                        op = data.get("op")
                        if op == 10:
                            heartbeatInterval = data["d"]["heartbeat_interval"]
                            self._logger.info(f"WS > Start heartbeat: {heartbeatInterval}ms")
                            await ws.send(json.dumps({
                                "op": 2,
                                "d": {
                                    "token": self._token,
                                    "intents": 513,
                                    "properties": {
                                        "$os": "Windows",
                                        "$browser": "Chrome",
                                        "$device": ""
                                    }
                                }
                            }))
                            self._logger.info("WS > Identify sent")
                            asyncio.create_task(self._heartbeat(ws, heartbeatInterval))
                        elif data["t"] == "READY":
                            self._logger.info("WS > READY")
                            threading.Thread(target=ready, args=readyArgs+(data["d"]["static_client_session_id"],)).start()
                    except:
                        buffer = b""