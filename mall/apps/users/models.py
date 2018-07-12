from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,SignatureExpired,BadSignature
from django.conf import settings

# Create your models here.
class User(AbstractUser):

    mobile = models.CharField(verbose_name='手机号',unique=True,max_length=11)

    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='默认地址')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name




    def generic_email_token(self,email):

        serializer = Serializer(settings.SECRET_KEY,3600)

        token = serializer.dumps({'email':email,'id':self.id})

        return 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token.decode()

    @staticmethod
    def check_verify_token(token):

        serializer = Serializer(settings.SECRET_KEY, 3600)

        #token进行验证
        try:
            #resulst 结果是啥呢? 如果没有问题 {'email':email,'id':self.id}
            result = serializer.loads(token)
        except BadSignature:
            return None
        else:
            # return result.get('id')
            try:
                id = result.get('id')
                email = result.get('email')
                # filter().filter()
                user = User.objects.get(id=id)
            except User.DoesNotExist:
                return None

            return user

from utils.models import BaseModel

class Address(BaseModel):
    """
    用户地址
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']





