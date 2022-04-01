import requests

from .official import __api__


class LegymRequester:
    def __init__(self) -> None:
        """读取配置。"""
        self.__headers = {"content-type": "application/json"}
        self.__api_dict = __api__

    def __str__(self) -> str:
        return "<Legym Requester>"

    def __repr__(self) -> str:
        return "<Legym Requester>"

    def request(self, api_name: str) -> dict:
        """发起请求，并返回 JSON 形式的响应。"""
        if api_name.startswith('http'):
            response = requests.request(
                method='get',
                url=api_name,
                headers=self.__headers,
            )
            return response.json()
            
        api = self.__api_dict[api_name]
        response = requests.request(
            method=api["method"],
            url=api["url"],
            headers=self.__headers,
            json=api["data"],
        )
        return response.json()

    def update_header(self, new_header: dict) -> None:
        """更新请求头。"""
        self.__headers.update(new_header)

    def update_api(self, api_name: str, new_data: dict) -> None:
        """更新指定 API 的 POST 数据。"""
        cur_data: dict = self.__api_dict[api_name]["data"]
        cur_data.update(new_data)
