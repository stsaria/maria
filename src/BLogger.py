class BLogger:
    def __init__(self, token:str):
        self._token:str = token.split(".")[0]
    def info(self, msg) -> None:
        print(f"({self._token}) " + msg)
    def warn(self, msg) -> None:
        print(f"\033[33mWarn: ({self._token}) " + msg)
    def error(self, msg) -> None:
        print(f"\033[31mError: ({self._token}) " + msg)