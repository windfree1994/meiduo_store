def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }

import re
from users.models import User
from django.contrib.auth.backends import ModelBackend

def get_user_by_account(username):

    try:
        if re.match(r'1[3-9]\d{9}',username):
            user = User.objects.get(mobile=username)
        else:
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None

    return user
#定义 一个多账号登陆的类 继承自Modelbackend 使 手机号也可以去登陆
class UsernameMobileAuthBackend(ModelBackend):
    """
    用户输入用户名或手机号后  恩局用户输入的用户名（手机号）和密码进行校验 如果成功返回user
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        #user.check_password(password)通过abstractuser 中的方法检测密码
        if user is not None and user.check_password(password):
            return user