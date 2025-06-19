import asyncio
import json
import random
import threading
import time
import typing
import uuid

import requests.models

from src.Proxy import Proxy
from src.AdvRequests import AdvRequests
from src.selfBot.AnalyzerForDiscord import AnalyzerForDiscord
from src.selfBot.DisguiseUtils import DisguiseUtils
from src.selfBot.DiscordWebSocket import DiscordWebSocket
from src.BLogger import BLogger
from src.selfBot.infos.Guild import Guild

BASE_API_URL = "https://discord.com/api/v9/"

class Bot:
    def __init__(self, token:str, proxy:Proxy | None = None, capmonsterKey:str | None = None):
        self._token = token
        self._advReq = AdvRequests(proxy)
        DisguiseUtils.advReq = self._advReq
        self._clientLaunchId = str(uuid.uuid4())
        self._ws = DiscordWebSocket(token, self._clientLaunchId)
        self._headers = {}
        self._logger:BLogger = BLogger(token)
        self.started = False
        self._capmonsterKey:str = capmonsterKey

        self._guilds:typing.Dict[int:Guild] = {}

    def _get(self, url) -> requests.models.Response:
        return self._advReq.get(BASE_API_URL+url, headers=self._headers)
    def _post(self, url, data:typing.Dict[str, str | bytes | None]) -> requests.models.Response:
        return self._advReq.post(BASE_API_URL+url, data=data, headers=self._headers)
    def _sendToWs(self, data:dict) -> None:
        self._ws.send(json.dumps(data))
    def sendMessage(self, channelId:int, msg:str, tts:bool=False):
        r = self._post(f"channels/{channelId}/messages", {
            "content": msg,
            "nonce": str(random.randint(10**18, 10**18 + 2*(10**17))),
            "tts": tts
        })
        print(r.json())
        if r.status_code == 429:
            self._logger.error("Too many Requests")
        elif str(r.status_code)[0] == "2":
            self._logger.info("Success")
        else:
            self._logger.error("Unknow Failed")
    def _joinedGuild(self):
        pass
    def joinGuild(self, invite:str):
        xContextProperties = DisguiseUtils.generateInviteXContextProperties(invite)
        if xContextProperties == "":
            self._logger.info("Incorrect invite")
        self._logger.info("Trying join guild")
        headers = self._headers.copy()
        headers["X-Context-Properties"] = xContextProperties
        print(headers)
        r = self._advReq.post(BASE_API_URL+f"invites/{invite}", {}, headers)
        if str(r.status_code)[0] == "2":
            self._logger.info("Success join guild")
            self._joinedGuild()
            return
        d = r.json()
        print(d)
        if r.status_code == 400 and "captcha_key" in d:
            self._logger.warn("Need HCaptcha")
            if not self._capmonsterKey:
                self._logger.error("Cant solve by capmonster (Key unavailable)")
                self._logger.error(f"Failed join guild")
                return
            r = self._advReq.post("https://api.capmonster.cloud/createTask", {
                "clientKey": self._capmonsterKey,
                "task": {
                    "type": "NoCaptchaTaskProxyless",  # プロキシなし（基本的にこれ）
                    "websiteURL": "https://discord.com/",
                    "websiteKey": "a9b5fb07-92ff-493f-86fe-352a2803b3df",
                    "enterprisePayload": {
                        "rqdata": d["captcha_rqdata"]
                    }
                }
            })
            taskId = r.json().get("taskId")
            if not taskId:
                self._logger.error("Couldn't solve by capmonster (failed create task)")
                return
            solve = ""
            while True:
                time.sleep(3)
                r = self._advReq.post("https://api.capmonster.cloud/getTaskResult", {
                    "clientKey": self._capmonsterKey,
                    "taskId": taskId
                })
                status = r.json().get("status")
                if status == "processing":
                    continue
                elif status == "ready":
                    self._logger.info("Solved HCaptcha")
                    solve = r.json()["solution"]["gRecaptchaResponse"]
                    break
                else:
                    self._logger.error("Couldn't Solve HCaptcha")
                    return
            r = self._post(f"invites/{invite}", {
                "captcha_key": solve,
                "captcha_rqtoken": d["captcha_rqdata"]
            })
            d = r.json()
            if str(r.status_code)[0] == "2":
                self._logger.info("Success join guild")
                self._joinedGuild()
                return
        self._logger.error(f"Failed join guild")
    def botStart(self, readyData:dict) -> None:
        self._headers = DisguiseUtils.generateHeaders(self._token, self._clientLaunchId, readyData["d"]["static_client_session_id"])
        self._advReq.get("https://discord.com/app", headers=self._headers)
        r = self._get("users/@me")
        if str(r.status_code)[0] != "2":
            self._logger.error(f"Bot > Token Dead - {self._token}")
            return
        self._logger.info("Bot > Started")
        self.started = True
    def wsStart(self):
        asyncio.run(self._ws.conn(Bot.botStart, (self,)))
    def start(self) -> None:
        threading.Thread(target=Bot.wsStart, args=(self,)).start()

DisguiseUtils.analyzer = AnalyzerForDiscord(AdvRequests())
bot = Bot("")
threading.Thread(target=Bot.start, args=(bot,)).start()
while True:
    if bot.started:
        break
bot.joinGuild("")
try:
    while True:
        pass
except KeyboardInterrupt:
    quit()