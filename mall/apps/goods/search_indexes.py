from haystack import indexes

from .models import SKU


class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    # document = True 每个searchindex需要有一个（也是唯一一个）字段
    #document = True这像Haystack和搜索引擎指示哪个字段是在其中搜索的主要字段
    #text 类似于新华字典的按照笔画或者按照拼音找到对应的页数
    # use_template = True  必须指定这一东西
    # # 我们需要指定一个模板 来规定 模型中的哪些字段可以作为 全文索引的字段
    # 模板路径必须满足 templates 下创建 search/indexes/应用名/应用名_text.txt

    #这允许我们使用数据模板（而不是容易出错的串联）来构建搜索引擎将索引的文档。
    # 您需要在调用的模板目录中创建一个新模板
    text = indexes.CharField(document=True, use_template=True)

    #以下字段用于数据展示  注意与model中一样
    id = indexes.IntegerField(model_attr='id')
    name = indexes.CharField(model_attr='name')
    price = indexes.DecimalField(model_attr='price')
    default_image_url = indexes.CharField(model_attr='default_image_url')
    comments = indexes.IntegerField(model_attr='comments')

    def get_model(self):
        """返回建立索引的模型类"""
        return SKU

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集"""
        return self.get_model().objects.filter(is_launched=True)
