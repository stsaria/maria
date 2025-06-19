import threading
import traceback
import typing

import websockets
import zlib
import json
import asyncio

from src.BLogger import BLogger
from src.ETF import ETF
from src.selfBot.DisguiseUtils import DisguiseUtils

ZLIB_SUFFIX = b"\x00\x00\xff\xff"

class DiscordWebSocket:
    def __init__(self, token:str, clientLaunchId:str):
        self._token = token
        self._decompressor = zlib.decompressobj()
        self.stop = False
        self._logger:BLogger = BLogger(token)
        self._sendMsg = None
        self._clientLaunchId = clientLaunchId
    async def _heartbeat(self, ws, interval):
        while True:
            await asyncio.sleep(interval / 1000)
            await ws.send(ETF.encode({"op": 1, "d": None}))
    def send(self, msg:str | dict):
        if type(msg) == str: msg = json.loads(msg)
        self._sendMsg = msg
    async def conn(self, ready:typing.Callable, readyArgs:tuple):
        async with websockets.connect("wss://gateway.discord.gg/?encoding=etf&v=9&compress=zlib-stream", additional_headers=DisguiseUtils.generateWSHeaders()) as ws:
            buffer = b""
            while True:
                if self.stop:
                    return
                if self._sendMsg:
                    await ws.send(ETF.encode(self._sendMsg))
                    self._sendMsg = None
                chunk = await ws.recv()
                if isinstance(chunk, str):
                    continue
                buffer += chunk
                if ZLIB_SUFFIX in buffer:
                    try:
                        msg = self._decompressor.decompress(buffer)
                        buffer = b""
                        data = ETF.decode(msg)
                        op = data.get("op")
                        if op == 10:
                            heartbeatInterval = data["d"]["heartbeat_interval"]
                            self._logger.info(f"WS > Start heartbeat: {heartbeatInterval}ms")
                            print(ETF.encode({
                                "op": 2,
                                "d": {
                                    "token": self._token,
                                    "capabilities": 161789,
                                    "properties": DisguiseUtils.generateWSIdentifyProperties(self._clientLaunchId),
                                    "presence": {
                                        "status": "unknown",
                                        "since": 0,
                                        "activities": [],
                                        "afk": False
                                    },
                                    "compress": False,
                                    "client_state": {
                                        "guild_versions": {}
                                    }
                                }
                            }).hex())
                            await ws.send(ETF.encode({
                                "op": 2,
                                "d": {
                                    "token": self._token,
                                    "capabilities": 161789,
                                    "properties": DisguiseUtils.generateWSIdentifyProperties(self._clientLaunchId),
                                    "presence": {
                                        "status": "unknown",
                                        "since": 0,
                                        "activities": [],
                                        "afk": False
                                    },
                                    "compress": False,
                                    "client_state": {
                                        "guild_versions": {}
                                    }
                                }
                            }))
                            self._logger.info("WS > Identify sent")
                            asyncio.create_task(self._heartbeat(ws, heartbeatInterval))
                        elif data["t"] == "READY":
                            self._logger.info("WS > READY")
                            threading.Thread(target=ready, args=readyArgs+(data,)).start()
                        else:
                            with open("aa.txt", mode="a") as f:
                                f.write(f"< {json.dumps(data)}\n\n")
                    except:
                        print(traceback.format_exc())
                        buffer = b""