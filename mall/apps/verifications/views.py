from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.views import APIView
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django.http import HttpResponse
from . import constants
from random import randint
from libs.yuntongxun.sms import CCP
from rest_framework.generics import GenericAPIView
from . serializers import RegisterSMSCodeserializer
from rest_framework.response import Response
class RegisterImageCodeView(APIView):
    """
    生成验证码 GET verifications/imagecodes/(?P<image_code_id>.+)/
    通过JS生成一个唯一码，以确保后台对图片进行校验
    """
    def get(self,request,image_code_id):
        """
        通过第三方库,生成图片和验证码,我们需要对验证码进行redis保存
        思路为:
        创建图片和验证码
        通过redis进行保存验证码,需要在设置中添加 验证码数据库选项
        将图片返回
        :param request:
        :param image_code_id:
        :return:
        """
        #创建图片和验证码
        text,image = captcha.generate_captcha()
        #通过redis进行保存验证码 code 是setting 中 redis设置的一个库
        redis_conn=get_redis_connection('code')
        #setex设置有效期
        redis_conn.setex('img_%s'%image_code_id,constants.IMAGE_CODE_EXPIPE_TIME,text)
        #返回图片 图片是二进制 所以用HttpResponse返回
        return HttpResponse(image,content_type='image/jpeg')

class RegisterSMSCodeView(GenericAPIView):
    """
    获取短信验证码
    GET   /verifications/smscodes/(?P<mobile>1[3-9]\d{9})/?text=xxxx&image_code_id=xxxx
    当点击按钮的时候应该吧验证码的内容发送过来进行校验
    校验成功后 给手机发送验证码
    将短信存起来 设置有效期
    需要设置发送的标记 防止用户频繁的操作
    """
    serializer_class = RegisterSMSCodeserializer
    def get(self,request,mobile):
        #验证码内容的校验（序列化器）
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        #判断用户是否已经有发送记录 ，防止用户频繁操作
        redis_conn = get_redis_connection('code')
        if redis_conn.get('sms_flag_%s' % mobile):
            return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)
        #生成短信验证码
        sms_code = '%06d' % randint(0, 999999)
        #记录发送状态
        # redis_conn.setex('sms_%s'%mobile,constants.SMS_CODE_EXIPRE_TIME,sms_code)
        #1 表示已经发送
        # redis_conn.setex('sms_flag_%s'%mobile,60,1)
        # 创建管道 将一行代码就执行一次redis操作 变成将管道中 的操作一起发送给redis-server  提高效率
        pl = redis_conn.pipeline()

        # 将我们的指令放到管道中 等待统一执行
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_EXIPRE_TIME, sms_code)
        pl.setex('sms_flag_%s' % mobile, 60, 1)

        # 执行
        pl.execute()
        #发 送
        # ccp = CCP()
        # ccp.send_template_sms(mobile,(sms_code,5),1)
        from celery_tasks.sms.tasks import send_sms_code
        send_sms_code.delay(mobile,sms_code)
        #由于我们的短信下发是同步操作的，同步操作有可能会出现等待的情况，造成响应不能及时返回
        #我们就直接采用celery  进行短信下发
        return Response({'message':'ok'})