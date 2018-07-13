from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView

from  goods.models import SKU
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
            'mobile':mobile
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

#邮箱激活
from rest_framework import status
class EmailVerifiView(APIView):
    def get(self,request):
        #获取激活token 判断token 是否存在
        token=request.query_params.get('token')
        #对token进行校验
        if token is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
            # 2.对token进行校验
            # 因为我不需要模型对象,所以把模型中的对象方法改为 类方法,静态方法
        user = User.check_verify_token(token)
        if user is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 3. 改变用户的邮件激活状态
        user.email_active = True
        user.save()

        return Response({'message': 'ok'})
        #改变用户的邮件激活状态


from .serializers import UserHistorySerializer,SKUSerializer
class UserHistoryView(APIView):
    """
    1.必须是登陆用户
    2.对传递的数据进行校验,将数据保存在redis中,
    3.我们是采用的list保存数据
    4。去重
    5.保留5条历史记录
     """
    #必须是登陆的用户
    permission_classes = [IsAuthenticated]
    def post(self,request):
        #创建序列化器 并且校验
        serializer=UserHistorySerializer(data=request.data,context={'request':request})
        serializer.is_valid()

        return Response(serializer.data)

    def get(self,request):

        """
         1.必须是登录用户
         2.根据指定用户获取指定的redis数据
         3. 通过序列化器 对数据进行 序列化操作
         4.返回数据
        """

        user = request.user

        redis_conn = get_redis_connection('history')

        sku_ids = redis_conn.lrange('history_%s'%user.id,0,5)
        # [1,2,3,4,5]

        skus = []

        for sku_id in sku_ids:

            sku = SKU.objects.get(pk=sku_id)

            skus.append(sku)

        # 3.通过序列化器对数据进行序列化操作
        serializer = SKUSerializer(skus,many=True)
        # 4.返回数据
        return Response(serializer.data)

