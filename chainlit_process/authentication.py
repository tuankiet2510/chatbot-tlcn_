from typing import Optional
import chainlit as cl
from repositories.user import auth_user

#decorator @cl.password_auth_callback regis hàm auth_callback gọi khi user xác thực bằng mật khẩu
# @cl.password_auth_callback decorator is used to register an authentication callback function that handles password-based user authentication.
@cl.password_auth_callback  # type: ignore
def auth_callback(username: str, password: str) -> Optional[cl.User]:
    user = auth_user(username, password)

    if not user:
        return None

    return cl.User(identifier=user.user_name, metadata={"user_id": str(user.id)}) # xác thực thành công
