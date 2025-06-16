import base64


class BLogger:
    def __init__(self, token:str):
        self._userId:int = int(base64.b64decode(token.split(".")[0]).decode())
    def info(self, msg) -> None:
        print(f"({self._userId}) " + msg)
    def error(self, msg) -> None:
        print(f"\033[31mError: ({self._userId}) " + msg)