from redis.exceptions import RedisError
from rest_framework import serializers
from django_redis import get_redis_connection
import logging
logger = logging.getLogger('meiduo')
#我们的序列化器没有关联的模型
class RegisterSMSCodeserializer(serializers.Serializer):
    text = serializers.CharField(label='用户输入的验证码', max_length=4, min_length=4)
    image_code_id = serializers.UUIDField(label='uuid')

    #字段的类型校验UUIDField
    #字段的选项 max_length=4
    #单个字段校验
    #多个字段校验
    def validate(self, attrs):
        #我们需要吧redis中的验证码获取出来后 进行校验
        #用户提交的验证码 拿到
        text= attrs.get('text')
        image_code_id=attrs.get('image_code_id')
        #链接获取
        redis_coon=get_redis_connection('code')
        redis_text=redis_coon.get('img_%s'%image_code_id)
        #判断是否过期
        if redis_text is None:
            raise serializers.ValidationError('验证码过期')
        #主动删除已经获取到的 redis中的数据
        try:
            redis_coon.delete('img_%s'%image_code_id)
        except RedisError as e:
            logger.error(e)
        # 字符串转小写
        if redis_text.decode().lower() != text.lower():
            raise serializers.ValidationError('验证码错误')
        return attrs
