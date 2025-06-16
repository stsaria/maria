import typing


class Cookies:
    def __init__(self):
        self._cookies:typing.Dict[str, str | bytes | None] = {}
    def sets(self, cookies:typing.Dict[str, str | bytes | None]) -> None:
        for k in cookies.keys():
            self._cookies[k] = cookies.get(k)
    def gets(self) -> typing.Dict[str, str | bytes | None]:
        return self._cookies.copy()
    def getsStr(self) -> str:
        s = ""
        for k in self._cookies.keys():
            s += f"{k}={self._cookies.get(k)}; "
        if s != "":
            s = s[:-1]
        return s