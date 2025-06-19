import platform
import re
import os
import locale
import sys

from src.AdvRequests import AdvRequests
from src.selfBot import Regexs


class AnalyzerForDiscord:
    def __init__(self, advReq:AdvRequests):
        self._platform = platform.system()
        self._osVersion = platform.release()
        self._releaseChannel = "ptb"
        self._browser = "Discord Client"
        self._advReq = advReq

        self._electronVersion:str | None = None
        self._chromeVersion:str | None = None
        self._latestDiscordBuildNumber:str | None = None
    def sAndR(self, name:str, value:object) -> str | object:
        setattr(self, name, value)
        return value
    def stringsAnalyzeAscii(self, fileName:str, regex:str, group:int=0) -> str:
        all:bytes = b""
        with open(fileName, 'rb') as f:
            all = f.read()
        found = re.findall(rb"[\x20-\x7E]{4,}", all)
        for s in found:
            s = s.decode('ascii', errors='ignore')
            s = re.search(regex, s)
            if s:
                return s.group(group)
        return ""
    def getPath(self) -> str | None:
        path = None
        match self._platform:
            case "Windows":
                path = os.path.isdir(os.getenv('LOCALAPPDATA')+"\\DiscordPTB\\")
            case "Linux":
                path = "/usr/share/discord-ptb/"
        if not os.path.isdir(path):
            path = None
        return path
    def getAppPath(self) -> str | None:
        basePath = self.getPath()
        if not basePath:
            return None
        path = None
        match self._platform:
            case "Windows":
                for fOrD in os.listdir(basePath):
                    if os.path.isfile(basePath+fOrD+"\\DiscordPTB.exe"):
                        path = basePath+fOrD
            case _:
                path = basePath
        if not os.path.isdir(path):
            path = None
        return path
    def getBin(self) -> str:
        match self._platform:
            case "Windows":
                return self.getAppPath()+ "\\DiscordPTB.exe"
            case _:
                return self.getAppPath()+ "/DiscordPTB"
    def getElectronVersion(self) -> str:
        if self._electronVersion: return self._electronVersion
        return self.sAndR("_electronVersion", self.stringsAnalyzeAscii(self.getBin(), Regexs.ELECTRON_VERSION_REGEX, group=1))
    def getChromeVersion(self) -> str:
        if self._chromeVersion: return self._chromeVersion
        return self.sAndR("_chromeVersion", self.stringsAnalyzeAscii(self.getBin(), Regexs.CHROME_VERSION_REGEX, group=1))
    def getNativeBuildNumber(self) -> int | None:
        if self._platform != "Windows": return None
        return int(self.stringsAnalyzeAscii(self.getPath()+"\\installer.db", Regexs.DISCORD_NATIVE_VERSION_REGEX, group=1))
    def getOsVersion(self) -> str:
        match self._platform:
            case "Windows":
                return platform.system()
            case _:
                return platform.release()
    def getReleaseChannel(self) -> str:
        return self._releaseChannel
    def getOs(self) -> str:
        return self._platform
    def getBrowser(self) -> str:
        return self._browser
    def getBrowserVersion(self) -> str:
        return self.getElectronVersion()
    def getSystemLocale(self) -> str:
        match self._platform:
            case "Windows":
                import ctypes
                return locale.windows_locale[ctypes.windll.kernel32.GetUserDefaultUILanguage()].split("_")[0]
            case _:
                return os.getenv('LANG').split("_")[0]
    def getClientVersion(self) -> str:
        return self.stringsAnalyzeAscii(self.getAppPath()+"/resources/build_info.json", Regexs.DISCORD_CLIENT_VERSION_REGEX, group=1)
    def getLatestDiscordBuildNumber(self) -> str | int:
        if self._latestDiscordBuildNumber: return self._latestDiscordBuildNumber
        r = self._advReq.get("https://ptb.discord.com/login")
        m = Regexs.SENTRY_ASSET_REGEX.search(r.text)
        if not m:
            return 0
        sentry = m.group(1)

        r = self._advReq.get(f"https://static.discord.com/assets/{sentry}.js")
        m = Regexs.BUILD_NUMBER_REGEX.search(r.text)
        if not m:
            return 0
        return self.sAndR("_latestDiscordBuildNumber", int(m.group(1)))
    def getArch(self) -> str:
        return {
            'amd64': 'x64',
            'x86_64': 'x64',
            'i386': 'x86',
            'i686': 'x86',
            'x86': 'x86',
            'arm64': 'arm64',
            'aarch64': 'arm64',
            'armv7l': 'arm32',
            'armv6l': 'arm32',
        }.get(platform.machine().lower(), "")
    def getWindowManager(self) -> str | None:
        if self._platform == "Linux":
            return "Unity,"+platform.freedesktop_os_release()["NAME"]
        return None
    def getDistro(self) -> str | None:
        if self._platform == "Linux":
            return platform.freedesktop_os_release()["PRETTY_NAME"]
        return None
    def getUserAgentPlatform(self) -> str | None:
        match self._platform:
            case "Windows":
                winType = "Win64" if self.getArch() == "x64" else "Win32"
                return f"Windows NT {sys.getwindowsversion().major}.{sys.getwindowsversion().minor}; {winType}; {self.getArch()}"
            case "Linux":
                return f"X11; Linux {platform.machine()}"
            case "Darwin":
                return "Macintosh; Intel Mac OS X "+platform.mac_ver()[0].replace(".", "_")
        return None
    def getWindowsSdkBuildNumber(self) -> str | None:
        if self._platform != "Windows": return None
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows Kits\Installed Roots"
        )
        sdkRoot, _ = winreg.QueryValueEx(key, "KitsRoot10")
        winreg.CloseKey(key)
        libPath = os.path.join(sdkRoot, "Lib")
        if not os.path.exists(libPath): return None
        versions = [
            d for d in os.listdir(libPath)
            if re.match(Regexs.WINDOWS_SDK_VERSION, d)
        ]
        if not versions: return None
        latest = sorted(versions, reverse=True)[0]
        match = re.search(Regexs.WINDOWS_SDK_VERSION, latest)
        if match:
            return match.group(1)
        return None
