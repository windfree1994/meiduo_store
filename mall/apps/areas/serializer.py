#coding:utf8
from rest_framework import serializers
from .models import Area


class AreaSerialzier(serializers.ModelSerializer):

    class Meta:
        model = Area
        fields = ['id','name']


class SubsAreaSeriazlier(serializers.ModelSerializer):
    # 市 区县的模型数据 用 AreaSerialzier 进行序列化操作
    #area_set = AreaSerialzier(many=True,read_only=True)
    subs = AreaSerialzier(many=True,read_only=True)

    class Meta:
        model = Area
        fields = ['id','name','subs']


