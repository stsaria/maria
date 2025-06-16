import typing
import requests
import urllib.parse

from src.Proxy import Proxy
from src.Cookies import Cookies

class AdvRequests:
    def __init__(self, proxy:Proxy | None):
        self._cookiesS:typing.Dict[str, Cookies] = {}
        self._proxy = proxy
    def request(self, method:str, url:str, data:typing.Dict[str, str | bytes | None], headers:typing.Dict[str, str | bytes | None]) -> requests.Response:
        domain = urllib.parse.urlparse(url).netloc
        if not domain in self._cookiesS.keys():
            self._cookiesS[domain] = Cookies()
        proxies = None
        auth = None
        if self._proxy:
            proxies = self._proxy.getProxies()
            auth = self._proxy.getAuth()
        headers["Cookie"] = self._cookiesS[domain].getsStr()
        r = requests.request(method=method, url=url, data=data, headers=headers, proxies=proxies, auth=auth)
        dCookies = {}
        for k in r.cookies.keys():
            dCookies[k] = r.cookies.get(k)
        self._cookiesS[domain].sets(dCookies)
        return r
    def get(self, url, headers=None):
        if not headers:
            headers = {}
        return self.request("get", url, data={}, headers=headers)
    def post(self, url:str, data:typing.Dict[str, str | bytes | None], headers:typing.Dict[str, str | bytes | None] = None):
        if not headers:
            headers = {}
        return self.request("post", url, data=data, headers=headers)