from rest_framework import serializers
from .models import User
from django_redis import get_redis_connection
#有关联的模型 数据入库直接调用create 方法 不用自己手动实现
class CreateUserSerializer(serializers.ModelSerializer):
   #吧用户名 密码 密码2（确认密码）  手机号  短信验证码 是否同意协议 post给我们
    password2=serializers.CharField(label='确认密码',write_only=True,allow_null=False,allow_blank=False)


    sms_code = serializers.CharField(label='短信验证码', max_length=6, min_length=6, allow_null=False, allow_blank=False,
                                 write_only=True)
    allow = serializers.CharField(label='是否同意协议', allow_null=False, allow_blank=False, write_only=True)
    class Meta:
        model=User
        fields=['username','password','mobile','sms_code','password2','allow']
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }
    # 吧用户名 密码 密码2（确认密码）  手机号  短信验证码 是否同意协议 post给我们
    #单个字段校验  手机号 ，是否同意协议
    def validate_mobile(self,value):
        import re
        if not re.match(r'1[3-9]\d{9}',value):
            raise serializers.ValidationError('手机号错误')
        return value
    def validate_allow(self,value):
        # 注意,前段提交的是否同意,我们已经转换为字符串
        if value != 'true':
            raise serializers.ValidationError('您未同意协议')

        return value
    #多个字段校验
    def validate(self, attrs):
        #判断用户密码是否一致
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError('密码不一致')
        #判断短信校验码
        # 获取redis中的验证码
        redis_conn = get_redis_connection('code')
        # 获取手机号码
        redis_code = redis_conn.get('sms_%s'%attrs.get ('mobile'))
        if redis_code is None:
            raise serializers.ValidationError('短信验证码过期')
        #redis数据是bytes类型
        #比对
        if redis_code.decode() != attrs.get('sms_code'):
            raise serializers.ValidationError('验证码不正确')

        return attrs
    def create(self, validated_data):

        #删除多余字段
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        user = super().create(validated_data)
        #数据 入库后 密码是明文的 所以 将密码 加密
        #修改密码
        user.set_password(validated_data['password'])
        user.save()

        return user