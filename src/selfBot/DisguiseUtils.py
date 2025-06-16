import json
import base64
from src.AdvRequests import AdvRequests
import Regexs


class DisguiseUtils:
    advReq:AdvRequests = None
    @classmethod
    def getLatestChromeVersion(cls) -> str:
        r = cls.advReq.get("https://versionhistory.googleapis.com/v1/chrome/platforms/win/channels/stable/versions")
        return r.json()['versions'][0]['version']
    @classmethod
    def getLatestDiscordBuildNumber(cls) -> int:
        r = cls.advReq.get("https://discord.com/login")
        m = Regexs.SENTRY_ASSET_REGEX.search(r.text)
        if not m:
            return 0
        sentry = m.group(1)

        r = cls.advReq.get(f"https://static.discord.com/assets/{sentry}.js")
        m = Regexs.BUILD_NUMBER_REGEX.search(r.text)
        if not m:
            return 0
        return int(m.group(1))
    @classmethod
    def generateXSuperProperties(cls, launchId:str, heartbeatSessionId:str) -> str:
        d = {
            "os":"Windows",
            "browser":"Chrome",
            "device":"",
            "system_locale":"ja",
            "has_client_mods":False,
            "browser_user_agent":f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{cls.getLatestChromeVersion()} Safari/537.36",
            "browser_version":cls.getLatestChromeVersion(),
            "os_version":"10",
            "referrer":"",
            "referring_domain":"",
            "referrer_current":"",
            "referring_domain_current":"",
            "release_channel":"stable",
            "client_build_number":cls.getLatestDiscordBuildNumber(),
            "client_event_source":None,
            "client_launch_id":launchId,
            "client_heartbeat_session_id":heartbeatSessionId,
            "client_app_state":"focused"
        }
        return base64.b64encode(json.dumps(d).encode()).decode()
    @classmethod
    def generateHeaders(cls, token:str, launchId:str, heartbeatSessionId:str):
        chromeMajorVersion = cls.getLatestChromeVersion().split(".")[0]
        d = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ja,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,ckb;q=0.6",
            "Authorization": token,
            "Priority": "u=1, i",
            "Referer": "https://discord.com/@me",
            "Sec-Ch-Ua": f'"Google Chrome";v="{chromeMajorVersion}", "Chromium";v="{chromeMajorVersion}", "Not/A)Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "ja", #todo: 設定ファイルにて設定
            "X-Discord-Timezone": "Asia/Tokyo", #todo: 設定ファイルにて設定
            "X-Super-Properties": cls.generateXSuperProperties(launchId, heartbeatSessionId),
        }
        return d