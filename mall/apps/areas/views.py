from django.shortcuts import render
from rest_framework import mixins
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializer import AreaSerialzier,SubsAreaSeriazlier
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Area
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin,RetrieveCacheResponseMixin,CacheResponseMixin
# Create your views here.

#ListCacheResponseMixin,        列表视图
#  RetrieveCacheResponseMixin,  详情视图
# CacheResponseMixin            列表+详情视图

class AreaView(CacheResponseMixin,ReadOnlyModelViewSet):

    """
    1. 地址页面必须登录用户才能显示

    2. 当我们点击新增地址的时候 省份信息已经获取了  获取省份信息   parent = None

    list        GET         areas/infos/

    3. 当我们确定省份信息的时候,应该 通过省份信息 获取 市的信息   parent = xxxx
         当我们确定市信息的时候,应该 通过市信息 获取 区(县)的信息   parent = xxxx

    retrieve    GET         areas/infos/pk



    省份
    10000           北京          None


    市
    10001           北京市         10000


    区县
    10010           昌平区         10001
    10020           海淀区         10001
    10030           朝阳区         10001

    """


    # queryset = 返回查询的结果集

    # queryset = Area.objects.all()
    #根据视图集执行的方法不同,返回不同的查询结果集
    # list  Area.ojbects.filter(parentid=None)

    # retrieve  Area.objects.all()

    def get_queryset(self):

        if self.action == 'list':
            # list 是省份信息
            return Area.objects.filter(parent=None)
        else:
            # retrieve 是 市 区县信息
            # 可以根据我们的 传递的id 获取指定信息
            return Area.objects.all()


    # serializer_class =

    def get_serializer_class(self):

        if self.action == 'list':
            return AreaSerialzier
        else:
            return SubsAreaSeriazlier

