#coding:utf8
def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user_id':user.id,
        'username':user.username
    }




from django.contrib.auth.backends import ModelBackend
import re
from users.models import User
#我们定义一个 多账号登录的类
# 这个类 继承自 ModelBackend
# 为什么呢? 因为就是懒 的 写 一个方法  get_user


def get_user_by_account(username):
    try:
        if re.match(r'1[3-9]\d{9}',username):
            # 用户输入的就是手机号
            user = User.objects.get(mobile=username)
        else:
            # 用户名
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None

    return user

class LoginUsernameMobileModelBackend(ModelBackend):



    def authenticate(self, request, username=None, password=None, **kwargs):

        """

        思路:
        用户输入用户名(手机号) 之后,
        我们根据 用户输入的用户名(手机号) 和密码 进行校验
        如果成功 返回user
        """

        user = get_user_by_account(username=username)

        #user.check_password(password 通过 AbstractUser 中的方法检测密码
        if user is not None and user.check_password(password):
            return user

        return None



class SettingsBackend(object):
    """
    Authenticate against the settings ADMIN_LOGIN and ADMIN_PASSWORD.

    Use the login name and a hash of the password. For example:

    ADMIN_LOGIN = 'admin'
    ADMIN_PASSWORD = 'pbkdf2_sha256$30000$Vo0VlMnkR4Bk$qEvtdyZRWTcOsCnI/oQ7fVOu1XAURIZYoOZ3iq8Dr4M='
    """

    def authenticate(self, request, username=None, password=None):
        user = get_user_by_account(username=username)

        # user.check_password(password 通过 AbstractUser 中的方法检测密码
        if user is not None and user.check_password(password):
            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
