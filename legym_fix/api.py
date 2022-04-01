from .user import LegymUser


def login(username: str, password: str) -> LegymUser:
    """登录乐健账号。

    Args:
        username: 用户名，一般是手机号。
        password: 密码。

    Returns:
        代表该用户的实例对象。
    """
    return LegymUser(username, password)
