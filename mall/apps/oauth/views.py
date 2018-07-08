from django.shortcuts import render
from django.conf import settings
from urllib.parse import urlencode
from rest_framework.response import Response
from .utlis import QQOauth
# Create your views here.
from rest_framework.views import APIView


class OauthQQURLView(APIView):
    """实现返回登陆QQ 的url
     # 生成auth_url
        # https://graph.qq.com/oauth2.0/authorize?拼接参数
        # 请求参数请包含如下内容：
        # response_type   必须      授权类型，此值固定为“code”。
        # client_id       必须      申请QQ登录成功后，分配给应用的appid。
        # redirect_uri    必须      成功授权后的回调地址，必须是注册appid时填写的主域名下的地址，建议设置为网站首页或网站的用户中心。注意需要将url进行URLEncode。
        # state           必须      client端的状态值。用于第三方应用防止CSRF攻击，成功授权后回调时会原样带回。请务必严格按照流程检查用户与state参数状态的绑定。
        # scope              可选      scope=get_user_info

    """

    def get(self, request):

        qq=QQOauth()
        auth_url=qq.get_oauth_url()

        return Response({'auth_url': auth_url})