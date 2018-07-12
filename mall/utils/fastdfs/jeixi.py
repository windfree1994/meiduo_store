from fdfs_client.client import Fdfs_client
#创建客户端
client =Fdfs_client('客户端的配置文件路径')#就是'utils/fastdfs/client.conf'
client.upload_by_filename('上传文件路径')#上传东西的绝对路径
"""
上传成功返回：
<fdfs_client.fdfs_protol.Tracker_header object at 0x7ff4429132b0>
{'Status': 'Upload successed.',
'Local file name': '/home/python/Desktop/shishi.jpg',
'Uploaded size': '19.00KB',
'Storage IP': '192.168.169.129',
'Remote file_id': 'group1/M00/00/00/wKipgVtHJXeAHygEAABNtKxAXUk592.jpg',这个是上传到storage的位置
'Group name': 'group1'}





"""