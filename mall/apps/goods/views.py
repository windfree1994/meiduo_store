from django.shortcuts import render
from django.views import View
from collections import OrderedDict
from .models import GoodsChannel,SKU
from contents.models import ContentCategory
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin,RetrieveCacheResponseMixin,CacheResponseMixin

# Create your views here.
class IndexVIew(View):
    def get(self,request):
        # 使用有序字典保存类别的顺序
        # categories = {
        #     1: { # 组1
        #         'channels': [{'id':, 'name':, 'url':},{}, {}...],
        #         'sub_cats': [{'id':, 'name':, 'sub_cats':[{},{}]}, {}, {}, ..]
        #     },
        #     2: { # 组2
        #
        #     }
        # }
        # 初始化存储容器
        categories = OrderedDict()
        # 获取一级分类
        channels = GoodsChannel.objects.order_by('group_id', 'sequence')

        # 对一级分类进行遍历
        for channel in channels:
            # 获取group_id
            group_id = channel.group_id
            # 判断group_id 是否在存储容器,如果不在就初始化
            if group_id not in categories:
                categories[group_id] = {
                    'channels': [],
                    'sub_cats': []
                }

            one = channel.category
            # 为channels填充数据
            categories[group_id]['channels'].append({
                'id': one.id,
                'name': one.name,
                'url': channel.url
            })
            # 为sub_cats填充数据
            for two in one.goodscategory_set.all():
                # 初始化 容器
                two.sub_cats = []
                # 遍历获取
                for three in two.goodscategory_set.all():
                    two.sub_cats.append(three)

                # 组织数据
                categories[group_id]['sub_cats'].append(two)
        # 广告和首页数据
        contents = {}
        content_categories = ContentCategory.objects.all()
        # content_categories = [{'name':xx , 'key': 'index_new'}, {}, {}]

        # {
        #    'index_new': [] ,
        #    'index_lbt': []
        # }
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')
    #加载末班 渲染数据
        context = {
            'categories': categories,
            'contents': contents
        }
        return render(request,'index.html', context)


from rest_framework.generics import ListAPIView
from .serializer import SKUSerializer
class HotSKUView(ListCacheResponseMixin,ListAPIView):
    """
      GET     /goods/categories/(?P<category_id>\d+)/hotskus/

      根据我们的分类进行 热销产品的查询,查询之后,进行序列化的操作

      """

    pagination_class = None

    serializer_class = SKUSerializer

    # queryset = SKU.objects.all()

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        # is_launched 判断是否上架,课下写的时候可以不写这个参数,因为主要的逻辑能够实现就行
        return SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2]



        # def get(self,request,category_id)


# from utils.pagintion import StandardResultsSetPagination
from rest_framework.filters import OrderingFilter
from utils.pagintion import StandardResultsSetPagination
class SKUListAPIView(ListAPIView):
    """
     GET /goods/categories/(?P<category_id>\d+)/skus/?page=xxx&page_size=xxx&ordering=xxx

        limit=xxx&offset=xxx
        from rest_framework.pagination import LimitOffsetPagination
    """

    # 序列化器
    serializer_class = SKUSerializer

    # 查询结果集
    # queryset =

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        # 只需要把 所有的商品信息获取到就可以
        return SKU.objects.filter(category_id=category_id, is_launched=True)
    #分页类
    pagination_class = StandardResultsSetPagination
    #排序
    filter_backends = [OrderingFilter]
    ordering_fields = ['create_time','price','sales']

from .serializer import SKUIndexSerializer
from drf_haystack.viewsets import HaystackViewSet

class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]

    serializer_class = SKUIndexSerializer




