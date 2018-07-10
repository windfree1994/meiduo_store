#coding:utf8
from rest_framework import serializers
from .models import OAuthQQUser
from django_redis import get_redis_connection
from users.models import User
# Serializer
# ModelSerialzer  -- 没有优势

class OauthQQSerializer(serializers.Serializer):

    access_token = serializers.CharField(label='操作token')
    mobile = serializers.RegexField(label='手机号', regex=r'^1[345789]\d{9}$')
    password = serializers.CharField(label='密码', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码', max_length=6, min_length=6)


    # def validate_moblie(self,value):


    def validate(self, attrs):


        # 验证用户提交的 access_token
        #aaaaa
        openid = OAuthQQUser.check_openid(attrs.get('access_token'))

        if openid is None:
            raise serializers.ValidationError('授权失败')
        # xxxx
        # 把 openid 添加到 attrs中 方便我们在 create中获取
        attrs['openid'] = openid

        # 验证短信码
        mobile = attrs['mobile']
        redis_conn = get_redis_connection('code')

        redis_code = redis_conn.get('sms_%s' % mobile)
        if redis_code.decode() != attrs['sms_code']:
            raise serializers.ValidationError('验证码错误')


        #我们需要根据手机号 需要再查找用户是否存在,如果已经存在,直接绑定这个用户就行
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            pass
        else:
            # 我们判断以下用户的密码是否输入正确
            if not user.check_password(attrs['password']):
                raise serializers.ValidationError('密码输入错误')

            #xxxxxx
            # 也把用户添加进去
            attrs['user'] = user

        return attrs


    def create(self, validated_data):


        # 我们需要给
        # OAuthQQUser.objects.create(
        #     openid=xxx,
        #     user=xxx
        # )

        user = validated_data.get('user')

        if user is None:
            #如果没有user 我们根据 用户提交的数据 创建user
            user = User.objects.create(
                mobile = validated_data.get('mobile'),
                password = validated_data.get('password'),
                username = validated_data.get('username')
            )

            user.set_password(validated_data.get('password'))
            user.save()


        #我们再把绑定数据插入到 qquser 表中
        qquser = OAuthQQUser.objects.create(
            openid=validated_data.get('openid'),
            user =user
        )

        return user