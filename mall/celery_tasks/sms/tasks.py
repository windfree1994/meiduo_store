from libs.yuntongxun.sms import CCP
from celery_tasks.main import app
#b吧任务单独抽取出来放在一个包中  包中的文件名 必须是tasks
#我们需要使用Celery的 对象装饰其来装饰该函数
@app.task(name='send_sms_code ')
def send_sms_code(mobile,sms_code):
    ccp = CCP()
    ccp.send_template_sms(mobile, (sms_code, 5), 1)