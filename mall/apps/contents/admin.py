# Register your models here.
from django.contrib import admin
from . import models
#定义管理模型类
# Register your models here.
admin.site.register(models.ContentCategory)
admin.site.register(models.Content)
