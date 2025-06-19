import typing

from src.selfBot.infos.Member import Member, MemberFormatter
from src.selfBot.infos.Channel import Channel, ChannelFormatter


class Guild:
    def __init__(self, id:int, name:str, members:typing.Dict[int,Member], channels:typing.Dict[int,Channel]):
        self._id:int = id
        self._name:str = name
        self._members:typing.Dict[int,Member] = members
        self._channels:typing.Dict[int,Channel] = channels
    def getId(self) -> int:
        return self._id
    def getName(self) -> str:
        return self._name
    def getMembers(self) -> typing.List[Member]:
        return [self._members[k] for k in self._members.keys()]
    def getMemberFromId(self, id:int) -> Member:
        return self._members.get(id)
    def getChannels(self) -> typing.List[Channel]:
        return [self._channels[k] for k in self._channels.keys()]
    def getChannelFromId(self, id:int):
        return self._channels.get(id)

class GuildFormatter:
    @staticmethod
    def gatewayReadyJsonToGuild(d:dict) -> Guild:
        members:dict[int:Member] = {m["user"]["id"]: MemberFormatter.gatewayReadyJsonToMember(m) for m in d["members"]}
        channels:dict[int:Channel] = {}
        for c in d["channels"]:
            if c["type"] != 0:
                continue
            channels[c["id"]]: ChannelFormatter.gatewayReadyJsonToChannel(c)
        return Guild(d["id"], d["name"], members, channels)


