import random
from datetime import datetime, timedelta

from .activities import LegymActivities
from .requester import LegymRequester


class LegymUser(LegymRequester):
    def __init__(self, username: str, password: str) -> None:
        """初始化用户。"""
        super().__init__()
        
        self.__request_login(username, password)
        self.__request_semester()
        self.__request_limit()
        # self.__activities = self.get_activities()

    def __str__(self) -> str:
        return f"<Legym User {self.__real_name}>"

    def __repr__(self) -> str:
        return f"<Legym User {self.__real_name}>"

    def __request_login(self, username: str, password: str) -> None:
        """请求登录站点，并更新 API 数据。"""
        self.update_api("login", {"userName": username, "password": password})
        response = self.request("login")["data"]
        self.__real_name = response["realName"]
        self.__nick_name = response["nickName"]
        self.__school = response["schoolName"]
        self.__organization = response["organizationName"]

        self.update_header(
            {
                "authorization": f"Bearer {response['accessToken']}",
                "Organization": response["schoolId"],
            }
        )
        self.update_api("sign", {"userId": response["id"]})

    def __request_semester(self) -> None:
        """请求学期站点，并更新 API 数据。"""
        response = self.request("semester")["data"]
        semester_id: str = response["id"]
        self.update_api("limit", {"semesterId": semester_id})
        self.update_api("running", {"semesterId": semester_id})

    def __request_limit(self) -> None:
        """请求上限站点，并更新 API 数据。"""
        response = self.request("limit")["data"]
        limit_id: str = response["limitationsGoalsSexInfoId"]
        self.__limit: float = response["effectiveMileageEnd"]
        self.update_api("running", {"limitationsGoalsSexInfoId": limit_id})

    def __request_register(self, activity_id: str) -> tuple:
        """请求报名站点，并返回结果和原因。"""
        self.update_api("register", {"activityId": activity_id})
        response = self.request("register")["data"]
        return response["success"], response["reason"]

    def __request_sign(self, activity_id: str) -> str:
        """请求签到站点，并返回结果和原因。"""
        self.update_api("sign", {"activityId": activity_id})
        response = self.request("sign")
        return response["code"] == 0, response["message"]

    def get_activities(self) -> LegymActivities:
        """获取活动列表。"""
        response = self.request("activities")["data"]
        for activity in response['items']:
            id_ = activity['id']
            resp = self.request(f'https://cpes.legym.cn/education/app/activity/checkSignInterval?activityId={id_}')
            interval = resp['data']['timeInterval']
            if interval is not None:
                interval = float(resp['data']['timeInterval']) / 60000
            activity['timeInterval'] = interval
            
        return LegymActivities(response["items"])

    def register(
        self, id: str = "", code: str = "", name: str = ""
    ) -> tuple:
        """报名活动。

        Args:
            id: 活动 ID。
            code: 活动代码，即 ID 最后四位。
            name: 活动名称。

        Returns:
            - [0] 实际报名的活动名称。
            - [1] 成功为 `True`，失败为 `False`。
            - [2] 成功或失败的原因。
        """
        self.__activities = self.get_activities()
        qualified = self.__activities.search(
            id=id, code=code, name=name, state="available"
        )
        if qualified == []:
            return "", False, f"没有找到可报名的活动"

        success, reason = self.__request_register(qualified[0].id)
        return qualified[0].name, success, reason

    def sign(
        self, id: str = "", code: str = "", name: str = ""
    ) -> list:
        """签到活动。

        Returns:
            若干个三元元组，每个元组包含下列信息。
            - [0] 签到的活动名称。
            - [1] 成功为 `True`，失败为 `False`。
            - [2] 成功或失败的原因。
        """
        self.__activities = self.get_activities()
        qualified = self.__activities.search(
            id=id, code=code, name=name, state="registered"
        ) + self.__activities.search(id=id, code=code, name=name, state="signed")
        if qualified == []:
            return "", False, "没有找到可签到的活动"

        results = []
        for activity in qualified:
            success, message = self.__request_sign(activity.id)
            results.append((activity.name, success, message))

        return results

    def run(self, distance: float = 0) -> tuple:
        """上传跑步数据。

        Args:
            distance: 要跑的里程，默认为每日上限。

        Returns:
            - [0] 实际跑的里程。
            - [1] 成功为 `True`，失败为 `False`。
        """
        if distance == 0:
            distance = self.__limit

        cost_time = random.randint(20, 30)
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=cost_time)
        self.update_api(
            "running",
            {
                "startTime": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "totalMileage": distance,
                "avePace": cost_time * 60 / distance * 1000,
                "calorie": int(distance * random.uniform(70.0, 75.0)),
                "effectiveMileage": distance,
                "endTime": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "gpsMileage": distance,
                "paceNumber": distance * (random.randint(50, 150)),
                "paceRange": random.randint(5, 10),
            },
        )

        response = self.request("running")["data"]
        return distance, response

    @property
    def real_name(self) -> str:
        return self.__real_name

    @property
    def nick_name(self) -> str:
        return self.__nick_name

    @property
    def school(self) -> str:
        return self.__school

    @property
    def organization(self) -> str:
        return self.__organization
