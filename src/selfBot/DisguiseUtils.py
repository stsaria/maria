import json
import base64

import requests

from src.selfBot.AnalyzerForDiscord import AnalyzerForDiscord


class DisguiseUtils:
    analyzer:AnalyzerForDiscord = None
    @classmethod
    def generateUserAgent(cls) -> str:
        return f"Mozilla/5.0 ({cls.analyzer.getUserAgentPlatform()}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{cls.analyzer.getChromeVersion()} Electron/{cls.analyzer.getElectronVersion()} Safari/537.36"

    @classmethod
    def generateXSuperProperties(cls, launchId:str, heartbeatSessionId:str) -> str:
        d = {
            "os":cls.analyzer.getOs(),
            "browser":cls.analyzer.getBrowser(),
            "release_channel":cls.analyzer.getReleaseChannel(),
            "client_version":cls.analyzer.getClientVersion(),
            "os_version":cls.analyzer.getOsVersion(),
            "os_arch":cls.analyzer.getArch(),
            "app_arch":cls.analyzer.getArch(),
            "system_locale":cls.analyzer.getSystemLocale(),
            "has_client_mods":False,
            "client_launch_id":launchId,
            "browser_user_agent":cls.generateUserAgent(),
            "browser_version":cls.analyzer.getElectronVersion(),
            "client_build_number":cls.analyzer.getLatestDiscordBuildNumber(),
            "native_build_number":cls.analyzer.getNativeBuildNumber(),
            "client_event_source":None,
            "client_heartbeat_session_id":heartbeatSessionId,
            "client_app_state":"focused"
        }
        match cls.analyzer.getOs():
            case "Linux":
                d["window_manager"] = cls.analyzer.getWindowManager()
                d["distro"] = cls.analyzer.getDistro()
            case "Windows":
                d["os_sdk_version"] = cls.analyzer.getWindowsSdkBuildNumber()
        print(d)
        return base64.b64encode(json.dumps(d).encode()).decode()
    @classmethod
    def generateWSIdentifyProperties(cls, launchId:str) -> dict:
        d:dict = json.loads(base64.b64decode(cls.generateXSuperProperties(launchId, "")))
        d["is_fast_connect"] = False
        d["latest_headless_tasks"] = []
        d["latest_headless_task_run_seconds_before"] = None
        d["gateway_connect_reasons"] = "AppSkeleton"
        d.pop("client_heartbeat_session_id")
        return d
    @classmethod
    def generateHeaders(cls, token:str, launchId:str, heartbeatSessionId:str):
        chromeMajorVersion = cls.analyzer.getChromeVersion().split(".")[0]
        d = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "ja,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,ckb;q=0.6",
            "Authorization": token,
            "Priority": "u=1, i",
            "Referer": "https://ptb.discord.com/@me",
            "Sec-Ch-Ua": f'"Not/A)Brand";v="24", "Chromium";v="{chromeMajorVersion}"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": f'"{cls.analyzer.getOs()}"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": cls.generateUserAgent(),
            "X-Debug-Options": "bugReporterEnabled",
            "X-Discord-Locale": "ja", #todo: 設定ファイルにて設定
            "X-Discord-Timezone": "Asia/Tokyo", #todo: 設定ファイルにて設定
            "X-Super-Properties": cls.generateXSuperProperties(launchId, heartbeatSessionId)
        }
        return d
    @classmethod
    def generateInviteXContextProperties(cls, invite:str):
        r = requests.get(f"https://discord.com/api/v9/invites/{invite}")
        if str(r.status_code)[0] != "2":
            return ""
        d = r.json()
        if d["type"] != 0:
            return ""
        pD = {
            "location": "Accept Invite Page",
            "location_guild_id": d["guild"]["id"],
            "location_channel_id": d["channel"]["id"],
            "location_channel_type": d["channel"]["type"]
        }
        return base64.b64encode(json.dumps(pD).encode()).decode()
    @classmethod
    def generateWSHeaders(cls) -> dict:
        return {"User-Agent": cls.generateUserAgent()}