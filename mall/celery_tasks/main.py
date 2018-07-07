#celery 步骤：
#1创建celery 对象
from celery import Celery
#celery_tasks是一个一步人物放哪都可以执行 但有一定的局限性
#我们需要将工程的setting 文件添加到系统中
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mall.settings'

#main 给celery起一个名字 这个名字建议采用脚本路径
#main也可以不设置
app=Celery('celert_task')

#2 通过celery 对象来加载配置文件这个配置文件其实就是设置broker
#我们需要通过celery 来设置Broker
#通过加载配置文件来设置 参数是脚本名.文件名
app.config_from_object('celery_tasks.config')
#我们要让celery 自动检测任务
#tasks 是个复数形式 可以检测多个任务--》参数就是列表
#列表中的每一项需要满足：脚本路径。包名
app.autodiscover_tasks(['celery_tasks.sms'])
#worker  执行是通过指令，自动去执行
#celery - A 脚本路径.celery的实力文件 worker -l info
#celery -A celery_tasks.main worker -l info   虚拟环境中执行c