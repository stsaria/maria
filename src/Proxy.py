import typing

import requests.auth


class Proxy:
    def __init__(self, proxies:typing.Dict[str, str], auth:requests.auth.HTTPProxyAuth | requests.auth.HTTPDigestAuth):
        self._proxies = proxies
        self._auth = auth
    def getProxies(self) -> typing.Dict[str, str]:
        return self._proxies
    def getAuth(self) -> requests.auth.HTTPProxyAuth | requests.auth.HTTPDigestAuth:
        return self._auth