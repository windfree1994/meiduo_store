from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings
from django.utils.deconstruct import deconstructible

#4.您的存储类必须是可解构的，
# 以便在迁移中的字段上使用时可以对其进行序列化。
# 只要您的字段具有可自行序列化的参数，就 可以使用
#  django.utils.deconstruct.deconstructible类装饰器
# （这就是Django在FileSystemStorage上使用的）。

#1\您的自定义存储系统必须是以下子类 django.core.files.storage.Storage：
@deconstructible
class MyStorage(Storage):
    #2\Django必须能够在没有任何参数的情况下实例化您的存储系统。
    # 这意味着任何设置都应该来自django.conf.settings：
    def __init__(self, option=None):
        pass



    #3.1您的存储类！！必须实现_open()和_save()！！！ 方法以及适用于您的存储类的任何其他方法。
    #open打开文件的方法 我们采用的是fastdfs的storage实现的文件下载所以不需要此方法
    #虽然不需要此方法 但是要求必须实现 所以 不能删除 需要重写此方法
    def _open(self, name, mode='rb'):
        pass

    #3.2 保存方法  我们需要自己实现fastdfs 的文件上传
    def _save(self, name, content, max_length=None):
        #1  获取上传内容 content 就是上传的内容
        file_data=content.read()
        #2 通过fastdfs 上传    后面参数为 配置文件
        client=Fdfs_client(settings.FDFS_CLIENT_CONF)
        #或者将  配置文件作为参数传给init 方法 设置成一种属性
        result=client.upload_by_buffer(file_data)  #buffer 二进制流 通过content.read 拿到内容
        #3  判断上传结果 返回
        if result.get('Status')=='Upload successed.':
            #说明上传成功、
            return result.get('Remote file_id')
        else:
            raise Exception('上传失败')
    #我们采用的是FDFS 它有自己的文件存储系统如果上传相同的文件 他可以进行不重名处理  不会覆盖
    def exists(self, name):
        return False
    #url是返回文件的内容name就是我们通过文件上传的Remote file_id
    def url(self, name):
        return 'http://192.168.169.129:8888/'+ name