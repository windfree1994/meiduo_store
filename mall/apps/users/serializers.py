from rest_framework import serializers
from .models import User
from django_redis import get_redis_connection
from django.core.mail import send_mail
from django.conf import settings
#有关联的模型 数据入库直接调用create 方法 不用自己手动实现
class CreateUserSerializer(serializers.ModelSerializer):
   #吧用户名 密码 密码2（确认密码）  手机号  短信验证码 是否同意协议 post给我们
    password2=serializers.CharField(label='确认密码',write_only=True,allow_null=False,allow_blank=False)


    sms_code = serializers.CharField(label='短信验证码', max_length=6, min_length=6, allow_null=False, allow_blank=False,
                                 write_only=True)
    allow = serializers.CharField(label='是否同意协议', allow_null=False, allow_blank=False, write_only=True)
    token = serializers.CharField(label='登录状态token', read_only=True)  # 增加token字段
    class Meta:
        model=User
        fields=['id','username','password','mobile','sms_code','password2','allow','token']
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
        # 注册之后 也是 登陆  应该返回token
        # 手动创建token
        from rest_framework_jwt.settings import api_settings
        # 获取2个方法
        # 荷载方法
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        # 编码方法
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        # 将用户信息给 荷载
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token=token
        return user

class UserCenterInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')
class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email')
        extra_kwargs={
            'emali':{'requered':True}
        }

    def update(self, instance, validated_data):
        #获取邮箱
        email=validated_data.get('email')
        #保存数据
        instance.email=email
        instance.save()
        #发送激活邮件
        #这是同步发送邮件
        # subject = '美多商城注册邮件'
        # message = ''
        # from_email = settings.EMAIL_FROM
        # recipient_list = [email]
        # html_message = "<h1>激活邮件</h1>"
        # send_mail(subject=subject,
        #           message=message,
        #           from_email=from_email,
        #           recipient_list=recipient_list,
        #           html_message=html_message
        #           )
        verify_url = instance.generic_email_token(email)
        # subject = "美多商城邮箱验证"
        # html_message = '<p>尊敬的用户您好！</p>' \
        #                '<p>感谢您使用美多商城。</p>' \
        #                '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
        #                '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)
        # send_mail(subject, "", settings.EMAIL_FROM, [email], html_message=html_message)
        from celery_tasks.email.tasks import send_verify_email

        send_verify_email.delay(email,verify_url)


        return instance

from goods.models import SKU
from django_redis import get_redis_connection
class UserHistorySerializer(serializers.Serializer):
    sku_id=serializers.CharField(label='id')
    def validate(self, attrs):
        #判断sku_id是否存在
        sku_id=attrs.get('sku_id')
        try:
            sku=SKU.objects.get(pk=sku_id)
        except Exception:
            raise serializers.ValidationError('商品不存在')
        #保存到redis中
        redis_conn=get_redis_connection('history')
        #去重
        user=self.context['request'].user
        redis_conn.lrem('history_%s'%user.id,0,sku_id)
        redis_conn.lpush('history_%s' % user.id, sku_id)
        # 5.保留5条历史记录
        redis_conn.ltrim('history_%s' % user.id, 0, 4)

        return attrs

class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')

from users.models import Address
class AddressSerializer(serializers.ModelSerializer):

    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')


    def create(self, validated_data):
        #Address模型类中有user属性,将user对象添加到模型类的创建参数中
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """
    class Meta:
        model = Address
        fields = ('title',)

