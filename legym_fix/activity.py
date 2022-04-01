from .requester import LegymRequester


class LegymActivity:
    def __init__(self, raw: dict) -> None:
        """解析出 JSON 中有用的字段。

        Args:
            activity: 乐健 API 返回的 JSON 数据。
        """
        self.__raw = raw
        self.__id = raw["id"]
        self.__name = raw["name"]
        self.__timeInterval = raw['timeInterval']
        if raw["performTime"] == 3:
            self.__state = "completed"
        elif raw["performTime"] == 2:
            self.__state = "signed"
        elif raw["performTime"] == 1:
            self.__state = "registered"
        elif raw["state"] == 0:
            self.__state = "blocked"
        elif raw["state"] in (1, 4):
            self.__state = "available"
        else:
            self.__state = "unknown"
        
        # req.update_api("checkTimeInterval", {"activityId": self.__id})
        # resp = req.request('checkTimeInterval')
        # print(resp)

    def __str__(self) -> str:
        return f"<Legym Activity id='{self.__id}' name='{self.__name}' state='{self.__state}'>"

    def __repr__(self) -> str:
        return f"<Legym Activity id='{self.__id}' name='{self.__name}' state='{self.__state}'>"

    @property
    def raw(self):
        return self.__raw
    
    @property
    def id(self) -> str:
        return self.__id

    @property
    def code(self) -> str:
        return self.__id[-4:]

    @property
    def name(self) -> str:
        return self.__name

    @property
    def state(self) -> str:
        return self.__state
    
    @property
    def timeInterval(self):
        return self.__timeInterval
