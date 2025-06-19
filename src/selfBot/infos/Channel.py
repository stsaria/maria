class Channel:
    def __init__(self, id:int, name:str, rateLimit:int):
        self._id:int = id
        self._name:str = name
        self._rateLimit:int = rateLimit
    def getId(self) -> int:
        return self._id
    def getName(self) -> str:
        return self._name
    def getRateLimit(self) -> int:
        return self._rateLimit

class ChannelFormatter:
    @staticmethod
    def gatewayReadyJsonToChannel(d:dict) -> Channel:
        return Channel(d["id"], d["name"], d["display_name"])