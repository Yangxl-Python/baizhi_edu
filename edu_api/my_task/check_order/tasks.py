import logging
from datetime import datetime

from edu_api.settings.constans import ORDER_EXPIRE_TIME
from my_task.main import app
from order.models import Order


@app.task(name="check_order")
def check_order():
    """
    完成过期取消订单
    根据时间点判断订单支付时间是否超时
    """
    now = datetime.now().timestamp()
    out_time = datetime.fromtimestamp(now - ORDER_EXPIRE_TIME)
    count = 0
    try:
        order_list = Order.objects.filter(is_show=True, is_delete=False, order_status=0, create_time__lte=out_time)
        for order in order_list:
            order.order_status = 3
            order.save()
            count += 1
        return f'set timeout succeeded，count:{count}'
    except Exception as e:
        logging.error(e)
        return 'fail'
