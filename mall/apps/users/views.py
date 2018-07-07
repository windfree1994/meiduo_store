from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from .models import User
from .serializers import CreateUserSerializer
# Create your views here.
from rest_framework.views import APIView


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