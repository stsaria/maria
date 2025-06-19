from src.selfBot.infos.User import User, UserFormatter


class Member:
    def __init__(self, user:User, roles:list[int], nick:str | None):
        self._user:User = user
        self._roles:list[int] = roles
        self._nick:str | None = nick
    def getUser(self) -> User:
        return self._user
    def getRoles(self) -> list[int]:
        return self._roles
    def getNick(self) -> str | None:
        return self._nick

class MemberFormatter:
    @staticmethod
    def gatewayReadyJsonToMember(d:dict) -> Member:

        return Member(UserFormatter.gatewayReadyJsonToUser(d["user"]), d["roles"], d["nick"])