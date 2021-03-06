from django.db import models

from home.BaseModel import BaseModel
from user.models import UserInfo

from course.models import Course
from edu_api.settings.constans import HOST


class Order(BaseModel):
    """订单模型"""
    status_choices = (
        (0, '未支付'),
        (1, '已支付'),
        (2, '已取消'),
        (3, '超时取消'),
    )
    pay_choices = (
        (1, '支付宝'),
        (2, '微信支付'),
    )
    order_title = models.CharField(max_length=150, verbose_name="订单标题")
    total_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="订单总价", default=0)
    real_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="实付金额", default=0)
    order_number = models.CharField(max_length=64, verbose_name="订单号")
    order_status = models.SmallIntegerField(choices=status_choices, default=0, verbose_name="订单状态")
    pay_type = models.SmallIntegerField(choices=pay_choices, default=1, verbose_name="支付方式")
    credit = models.IntegerField(default=0, verbose_name="使用的积分数量")
    coupon = models.IntegerField(null=True, verbose_name="用户优惠券ID")
    order_desc = models.TextField(max_length=500, verbose_name="订单描述")
    pay_time = models.DateTimeField(null=True, verbose_name="支付时间")
    user = models.ForeignKey(UserInfo, related_name='user_orders', on_delete=models.DO_NOTHING, verbose_name="下单用户")

    class Meta:
        db_table = "bz_order"
        verbose_name = "订单记录"
        verbose_name_plural = "订单记录"

    def __str__(self):
        return "%s,总价: %s,实付: %s" % (self.order_title, self.total_price, self.real_price)

    @property
    def order_username(self):
        return self.user.username

    @property
    def order_status_name(self):
        return self.status_choices[self.order_status][1]

    @property
    def pay_type_name(self):
        return self.pay_choices[self.pay_type-1][1]

    @property
    def order_detail_list(self):
        order_detail_list = OrderDetail.objects.filter(is_show=True, is_delete=False, order_id=self.id)

        data_list = []
        for order_detail in order_detail_list:
            data_list.append({
                'id': order_detail.id,
                'course_img': order_detail.course_img,
                'course_name': order_detail.course_name,
                'discount_name': order_detail.discount_name,
                'expire': order_detail.expire,
                'price': order_detail.price,
                'real_price': order_detail.real_price
            })

        return data_list


class OrderDetail(BaseModel):
    """
    订单详情
    """
    order = models.ForeignKey(Order, related_name='order_courses', on_delete=models.CASCADE, verbose_name="订单ID")
    course = models.ForeignKey(Course, related_name='course_orders', on_delete=models.CASCADE, verbose_name="课程ID")
    expire = models.IntegerField(default='0', verbose_name="有效期周期", help_text="0表示永久有效")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="课程原价")
    real_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="课程实价")
    discount_name = models.CharField(max_length=120, default="", verbose_name="优惠类型")

    class Meta:
        db_table = "bz_order_detail"
        verbose_name = "订单详情"
        verbose_name_plural = "订单详情"

    def __str__(self):
        return self.course.name

    @property
    def course_img(self):
        return f'{HOST}{self.course.course_img.url}'

    @property
    def course_name(self):
        return self.course.name
