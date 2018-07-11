from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from .models import User
from .serializers import CreateUserSerializer, UserCenterInfoSerializer
# Create your views here.
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class RegisterUsernameCountAPIView(APIView):
    """
    获取用户名的个数
    GET:  /users/usernames/(?P<username>\w{5,20})/count/
    """

    def get(self,request,username):

        #通过模型查询,获取用户名个数
        count = User.objects.filter(username=username).count()
        #组织数据
        context = {
            'count':count,
            'username':username
        }
        return Response(context)

class RegisterPhoneCountAPIView(APIView):
    """
    查询手机号的 个数
    GET: /users/phones/(?P<mobile>1[345789]\d{9})/count/
    """
    def get(self,request,mobile):
        #通过模型查询获取手机号个数
        count=User.objects.filter(mobile=mobile).count()
        context={
            'count':count,
            'phont':mobile
        }
        return Response(context)

class CreateUserView(CreateAPIView):
    """
    实现注册功能
    吧用户名 密码 手机号  短信验证码 是否同意协议 post给我们
    对数据进行校验
    验证之后 数据入库
    需求分析 【功能分析【参数和功能】-----确定HTTP请求方式----确定视图继承自谁】
    """
    serializer_class = CreateUserSerializer

#用户中心==个人 中心
#APIView  or   GenericaAPIView or  ListAPIView   RetrieveAPIView
# class UserCenterInfoView(APIView):
#     """
#     GET/users/infos/
#     获取用户信息  只有登陆用户才可以访问
#     """
#     permission_classes = [IsAuthenticated]
#     def get(self,request):
#          serializer=CreateUserSerializer(request.user)
#          return Response(serializer.data)
from rest_framework.generics import RetrieveAPIView
class UserCenterInfoView(RetrieveAPIView):
    """
    GET/users/infos/
    获取用户信息(指定用户的信息)  只有登陆用户才可以访问
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserCenterInfoSerializer
    #重写 get_object 方法
    def get_object(self):
        return self.request.user


from rest_framework.generics import UpdateAPIView
from .serializers import EmailSerializer

class EmailView(UpdateAPIView):
    """

    1. 当用户点击确定按钮的时候,把 邮箱发送给后台,邮箱需要校验
    2. 更新 用户的 邮箱信息
    3. 发送一个激活邮件(链接)
    4. 激活链接应该如何实现发送
    5. 邮件如何发送(代码怎么实现)
    6. 邮件采用celery异步发送

    """

    permission_classes = [IsAuthenticated]

    serializer_class = EmailSerializer

    def get_object(self):

        return self.request.user

