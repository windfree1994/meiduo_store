#coding:utf8
from rest_framework import serializers
from goods.models import SKU
class CartSerailzier(serializers.Serializer):

    sku_id = serializers.IntegerField(label='sku_id', required=True, min_value=1)
    count = serializers.IntegerField(label='数量', required=True, min_value=1)
    selected = serializers.BooleanField(label='是否勾选', required=False, default=True)


    def validate(self, attrs):

        # 判断商品id
        sku_id = attrs.get('sku_id')
        try:
            sku = SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')
        # 判断库存
        if sku.stock < attrs.get('count'):
            raise serializers.ValidationError('库存不足')

        return attrs





class CartSKUSerializer(serializers.ModelSerializer):

    count = serializers.IntegerField(label='数量')
    selected = serializers.BooleanField(label='是否勾选')

    class Meta:
        model = SKU
        fields = ('id','count', 'name', 'default_image_url', 'price', 'selected')

class CartDeleteSerializer(serializers.Serializer):

    sku_id = serializers.IntegerField(label='商品id',min_value=1)


    def validate(self, attrs):

        # 判断商品id
        sku_id = attrs.get('sku_id')
        try:
            sku = SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')

        return attrs