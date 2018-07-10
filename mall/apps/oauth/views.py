from django.shortcuts import render
from django.conf import settings
from urllib.parse import urlencode
from rest_framework.response import Response

from oauth.models import OAuthQQUser
from .utlis import QQOauth
# Create your views here.
from rest_framework.views import APIView
from urllib.request import urlopen


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

class OauthQQView(APIView):
    """
        # PC网站：https://graph.qq.com/oauth2.0/token
        # GET
        # grant_type      必须      授权类型，在本步骤中，此值为“authorization_code”。
        # client_id       必须      申请QQ登录成功后，分配给网站的appid。
        # client_secret   必须      申请QQ登录成功后，分配给网站的appkey。
        # code            必须      上一步返回的authorization
        # redirect_uri    必须      与上面一步中传入的redirect_uri保持一致。
    """
    def get(self,request):
        #获取code
        code=request.query_params.get('code')
        if code is None:
            return Response(status=400)
        qq = QQOauth()

        access_token=qq.get_access_token(code)

        openid=qq.get_openid(access_token)
        #根据openid来判断 用户是否绑定过
        try:
            qquse = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            #第一次授权 需要绑定
            return Response({'openid':openid})




