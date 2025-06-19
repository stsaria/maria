class User:
    def __init__(self, id:int, userName:str, displayName:str, globalName:str, isBot:bool):
        self._id:int = id
        self._userName:str = userName
        self._displayName:str = displayName
        self._globalName:str = globalName
        self._isBot:bool = isBot
    def getId(self) -> int:
        return self._id
    def getUserName(self) -> str:
        return self._userName
    def getDisplayName(self) -> str:
        return self._displayName
    def getGlobalName(self) -> str:
        return self._globalName
    def getIsBot(self) -> bool:
        return self._isBot

class UserFormatter:
    @staticmethod
    def gatewayReadyJsonToUser(d:dict) -> User:
        return User(d["id"], d["username"], d["display_name"], d["global_name"], d["bot"])
