from datetime import datetime
import random
import logging

from django.db import transaction
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from course.models import Course, CourseExpire
from order.models import Order, OrderDetail


class OrderModelSerializer(ModelSerializer):

    class Meta:
        model = Order
        fields = ('order_title', 'total_price', 'real_price', 'order_number', 'order_status_name',
                  'pay_type', 'pay_type_name', 'order_username', 'create_time')
        extra_kwargs = {
            'order_title': {
                'read_only': True
            },
            'total_price': {
                'read_only': True
            },
            'real_price': {
                'read_only': True
            },
            'order_number': {
                'read_only': True
            },
            'order_status_name': {
                'read_only': True
            },
            'pay_type': {
                'write_only': True
            },
            'pay_type_name': {
                'read_only': True
            },
            'order_username': {
                'read_only': True
            }
        }

    def create(self, validated_data):
        """生成订单   与  订单详情 """
        # 通过context获取到request对象
        request = self.context['request']
        user_id = request.user.id
        course_id = request.data.get('course_id')
        if course_id:
            return self.create_order_by_id(user_id, course_id, validated_data)

        redis_connection = get_redis_connection("cart")
        # 生成订单详情
        # 从购物车获取所有已勾选的商品
        select_list = redis_connection.smembers(f"selected_{user_id}")
        if not select_list:  # 判断购物车中已选择的商品是否为空
            raise serializers.ValidationError('当前已选择商品为空')
        cart_list = redis_connection.hgetall(f"cart_{user_id}")

        # 事务开启
        with transaction.atomic():
            # 记录下事务回滚的点
            rollback_id = transaction.savepoint()

            # 生成唯一的订单号  时间戳 用户id  随机字符串  0001  7862
            order_number = f'{datetime.now().strftime("%Y%m%d%H%M%S")}{user_id:06d}{random.randint(0, 999999):06d}'

            # 生成订单
            order = Order.objects.create(order_title="百知教育在线课程订单", total_price=0, real_price=0, is_show=True,
                                         order_number=order_number, pay_type=validated_data.get("pay_type"),
                                         order_desc="选择这个课程是你极其优秀的决定", user_id=user_id)

            for course_id_byte, expire_time_byte in cart_list.items():
                course_id = int(course_id_byte)
                expire_time = int(expire_time_byte)

                # 判断商品id是否在已勾选的的列表中
                if course_id_byte in select_list:
                    try:
                        # 获取到的所有的课程信息
                        course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
                    except Course.DoesNotExist:
                        """课程不存在则不再进行订单详情的生成 已生成好的订单表也不再保存"""
                        transaction.savepoint_rollback(rollback_id)
                        return serializers.ValidationError("对不起，当前商品不存在")

                    # 如果有效期的id大于0  则需要计算商品的价格  id不大于0则代表永久有效 需要默认值
                    original_price = course.price

                    try:
                        if expire_time > 0:
                            course_expire = CourseExpire.objects.get(course_id=course_id, expire_time=expire_time)
                            # 对应有效期的价格
                            original_price = course_expire.price
                    except CourseExpire.DoesNotExist:
                        transaction.savepoint_rollback(rollback_id)
                        return serializers.ValidationError("对不起，当前有效期不存在")

                    # 根据已勾选的商品的对应有效期的价格去计算勾选商品的最终价格
                    real_expire_price = course.real_expire_price(expire_time)
                    try:
                        # 生成订单详情
                        OrderDetail.objects.create(order=order, course=course, expire=expire_time, price=original_price,
                                                   real_price=real_expire_price, discount_name=course.discount_name,
                                                   is_show=True)
                    except Exception as e:
                        logging.error(e)
                        """回滚事务"""
                        transaction.savepoint_rollback(rollback_id)
                        raise serializers.ValidationError("订单生成失败")

                    # 计算订单的总价
                    order.total_price += float(original_price)
                    order.real_price += float(real_expire_price)

                    try:
                        # 删除购物车中的课程
                        redis_connection.hdel(f'cart_{user_id}', course_id)
                        redis_connection.srem(f'selected_{user_id}', course_id)
                    except Exception as e:
                        logging.warning(e)

            order.save()

            return order

    def create_order_by_id(self, user_id, course_id, validated_data):
        with transaction.atomic():
            # 记录下事务回滚的点
            rollback_id = transaction.savepoint()

            # 生成唯一的订单号  时间戳 用户id  随机字符串  0001  7862
            order_number = f'{datetime.now().strftime("%Y%m%d%H%M%S")}{user_id:06d}{random.randint(0, 999999):06d}'

            # 生成订单
            order = Order.objects.create(order_title="百知教育在线课程订单", total_price=0, real_price=0, is_show=True,
                                         order_number=order_number, pay_type=validated_data.get("pay_type"),
                                         order_desc="选择这个课程是你极其优秀的决定", user_id=user_id)

            try:
                # 获取到的对应的课程信息
                course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
            except Course.DoesNotExist:
                """课程不存在则不再进行订单详情的生成 已生成好的订单表也不再保存"""
                transaction.savepoint_rollback(rollback_id)
                return serializers.ValidationError("对不起，当前商品不存在")

            # 根据有效期的价格去计算勾选商品的最终价格
            real_expire_price = course.real_expire_price(0)
            try:
                # 生成订单详情
                OrderDetail.objects.create(order=order, course=course, expire=0, price=course.price,
                                           real_price=real_expire_price, discount_name=course.discount_name,
                                           is_show=True)
            except Exception as e:
                logging.error(e)
                """回滚事务"""
                transaction.savepoint_rollback(rollback_id)
                raise serializers.ValidationError("订单生成失败")

            order.total_price = float(course.price)
            order.real_price = float(real_expire_price)
            order.save()

        return order


class OrderListModelSerializer(ModelSerializer):

    class Meta:
        model = Order
        fields = ('create_time', 'order_number', 'order_status_name',
                  'order_detail_list')


class OneOrderModelSerializer(ModelSerializer):

    class Meta:
        model = Order
        fields = ()
