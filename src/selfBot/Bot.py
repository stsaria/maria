import asyncio
import uuid
from src.Proxy import Proxy
from src.AdvRequests import AdvRequests
from DisguiseUtils import DisguiseUtils
from DiscordWebSocket import DiscordWebSocket
from src.BLogger import BLogger


class Bot:
    def __init__(self, token:str, proxy:Proxy | None):
        self._token = token
        self._advReq = AdvRequests(proxy)
        DisguiseUtils.advReq = self._advReq
        self._clientLaunchId = uuid.uuid4().hex
        self._ws = DiscordWebSocket(token)
        self._headers = {}
        self._logger:BLogger = BLogger(token)
    def botStart(self, heartbeatSessionId:str):
        self._headers = DisguiseUtils.generateHeaders(self._token, self._clientLaunchId, heartbeatSessionId)
        self._advReq.get("https://discord.com/app", headers=self._headers)
        r = self._advReq.get("https://discord.com/api/v9/users/@me", headers=self._headers)
        if str(r.status_code)[0] != "2":
            self._logger.error(f"Bot > Token Dead - {self._token}")
            return
        self._logger.info("Bot > Started")
    def start(self):
        asyncio.run(self._ws.start(Bot.botStart, (self,)))
