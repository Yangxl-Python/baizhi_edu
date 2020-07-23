import logging

from edu_api.settings import constans
from edu_api.utils.send_msg import Message
from my_task.main import app

logger = logging.getLogger('django')


# celery的任务必须写在tasks的文件中，别的文件名称不识别
@app.task(name="send_sms")  # name可以指定当前任务的名称，如果不填写，则使用默认的函数名作为任务名
def send_sms(number, code):
    message = Message(constans.API_KEY)
    status = message.send_message(number, code)

    if not status:
        logger.error("用户发送短信失败，手机号为：%s" % number)
        return 'fail'

    return 'success'
