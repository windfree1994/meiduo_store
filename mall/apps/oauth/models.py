from django.db import models
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,BadTimeSignature,BadSignature
# Create your models here.
from django.db import models
from utils.models import BaseModel
from django.conf import settings

class OAuthQQUser(BaseModel):
    """
    QQ登录用户数据
    """
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name

    @classmethod
    def genericte_openid_token(cls,openid):

        #创建序列化器
        serializer=Serializer(settings.SECRET_KEY,3600)
        #对数据进行处理
        token=serializer.dumps({'openid':openid})
        return token.decode()

    @classmethod
    def check_openid(cls,token):
        serializer=Serializer(settings.SECRET_KEY,3600)
    #根据校验 需要进行try catch操作
        try:
            result=serializer.loads(token)
        except BadSignature:
            return None
        else:
            return result.get('openid')
