from .activity import LegymActivity


class LegymActivities:
    def __init__(self, raws: list) -> None:
        """将列表内的每个字典都解析为乐健活动。

        Args:
            raws: 乐健 API 返回的 JSON 列表。
        """
        self.__activities = [LegymActivity(raw) for raw in raws]

    def __str__(self) -> str:
        return "\n".join([str(activity) for activity in self.__activities])

    def __repr__(self) -> str:
        return "\n".join([str(activity) for activity in self.__activities])

    def search(
        self, id: str = "", code: str = "", name: str = "", state: str = ""
    ) -> list:
        """根据自定义规则筛选活动。

        Args:
            id: 活动 ID。
            code: 活动代码，即活动 ID 的最后 4 位。
            name: 活动名称。
            state: 活动状态。

        Returns:
            筛选出的活动列表。
        """
        results = self.__activities.copy()

        if id != "":
            results = list(filter(lambda act: act.id == id, results))
        if code != "":
            results = list(filter(lambda act: act.code == code, results))
        if name != "":
            results = list(filter(lambda act: act.name.find(name) != -1, results))
        if state != "":
            results = list(filter(lambda act: act.state == state, results))

        return results
