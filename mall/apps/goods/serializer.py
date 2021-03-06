from rest_framework import serializers
from .models import SKU

class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')

from .search_indexes import SKUIndex
from drf_haystack.serializers import HaystackSerializer

class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """
    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'id', 'name', 'price', 'default_image_url', 'comments')