from enum import Enum

class ActionReturnType(Enum):
    TOO_MANY_REQUESTS = 1
    SUCCESS = 2
    UNKNOW_FAILED = 3
    INCORRECT_INVITE = 4