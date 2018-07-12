from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,SignatureExpired,BadSignature
from django.conf import settings

# Create your models here.
class User(AbstractUser):

    mobile = models.CharField(verbose_name='手机号',unique=True,max_length=11)

    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')


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





