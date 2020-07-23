import logging

from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated

from course.models import Course, CourseExpire
from edu_api.settings import constans

from edu_api.settings.constans import HOST

log = logging.getLogger()


class CartViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def add_cart(self, request, *args, **kwargs):
        course_id = request.data.get('course_id')
        user_id = request.user.id
        expire_time = 0

        try:
            Course.objects.get(is_show=True, id=course_id)
        except Course.DoesNotExist:
            return Response({'message': '课程不存在'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            conn = get_redis_connection('cart')
            pipeline = conn.pipeline()
            pipeline.multi()
            # 购物车内的商品
            pipeline.hset(f'cart_{user_id}', course_id, expire_time)
            # 被勾选的商品
            pipeline.sadd(f'selected_{user_id}', course_id)
            pipeline.execute()

            course_len = conn.hlen(f'cart_{user_id}')
        except Exception as e:
            log.error(e)
            return Response({'message': '添加失败'}, status=status.HTTP_507_INSUFFICIENT_STORAGE)

        return Response({'message': '添加成功', 'course_len': course_len})

    def cart_list(self, request, *args, **kwargs):
        user_id = request.user.id
        conn = get_redis_connection('cart')
        cart_list_b = conn.hgetall(f'cart_{user_id}')
        selected_list_b = conn.smembers(f'selected_{user_id}')

        data = []
        total = 0
        for course_id_b, expire_b in cart_list_b.items():
            course_id = int(course_id_b)
            expire_time = int(expire_b)
            try:
                course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
            except Course.DoesNotExist:
                continue

            selected = True if course_id_b in selected_list_b else False
            price = course.real_expire_price(expire_time)  # 根据当前有效期计算价格
            if selected:
                total += price
            data.append({
                'selected': selected,
                'course_img': f'{constans.HOST}{course.course_img.url}',
                'name': course.name,
                'id': course.id,
                'price': price,
                'expire_time': expire_time,
                'expire_list': course.expire_list
            })

        return Response({'cart_list': data, 'total_price': total})

    def change_select(self, request, *args, **kwargs):
        user_id = request.user.id
        selected = request.data.get('selected')
        course_id = request.data.get('course_id')

        try:
            Course.objects.get(is_show=True, is_delete=False, pk=course_id)
        except Course.DoesNotExist:
            return Response({'message': '参数有误，当前商品不存在'}, status=status.HTTP_400_BAD_REQUEST)

        conn = get_redis_connection('cart')
        if selected:
            conn.sadd(f'selected_{user_id}', course_id)
        else:
            conn.srem(f'selected_{user_id}', course_id)

        return Response({'message': '状态切换成功'})

    def change_expire(self, request):
        """改变redis中课程的有效期"""
        user_id = request.user.id
        expire_time = request.data.get("expire_time")
        course_id = request.data.get("course_id")

        try:
            course = Course.objects.get(is_show=True, is_delete=False, id=course_id)
            connection = get_redis_connection("cart")
            # 前端传递来的有效期时长 如果大于0 且数据库中存在 则修改课程对应的有效期
            if expire_time > 0:
                expire = CourseExpire.objects.get(is_show=True, is_delete=False, expire_time=expire_time,
                                                  course_id=course_id)
                connection.hset(f'cart_{user_id}', course_id, expire.expire_time)
            elif expire_time == 0:  # 0为永久有效
                connection.hset(f'cart_{user_id}', course_id, expire_time)
            else:
                return Response({"message": "有效期时长不能小于0"}, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            return Response({"message": "课程或有效期不存在"}, status=status.HTTP_400_BAD_REQUEST)

        real_expire_price = course.real_expire_price(expire_time)

        return Response({"message": "切换有效期成功", 'real_expire_price': real_expire_price})

    def delete_cart(self, request, *args, **kwargs):
        user_id = request.user.id
        course_id = request.data.get('course_id')

        try:
            conn = get_redis_connection('cart')
            conn.hdel(f'cart_{user_id}', course_id)
            conn.srem(f'selected_{user_id}', course_id)
        except Exception as e:
            log.error(e)
            return Response({'message': '删除失败或商品已被删除'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': '删除成功'})

    def get_select_course(self, request, *args, **kwargs):
        """
        获取购物车中已勾选的商品  返回前端所需的数据
        """

        user_id = request.user.id
        redis_connection = get_redis_connection("cart")

        # 获取当前登录用户的购车中所有的商品
        cart_list = redis_connection.hgetall("cart_%s" % user_id)
        select_list = redis_connection.smembers("selected_%s" % user_id)

        total_price = 0  # 商品总价
        data = []

        for course_id_byte, expire_time_byte in cart_list.items():
            course_id = int(course_id_byte)
            expire_time = int(expire_time_byte)

            # 判断商品id是否在已勾选的的列表中
            if course_id_byte in select_list:
                try:
                    # 获取到的所有的课程信息
                    course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
                except Course.DoesNotExist:
                    continue
                # 如果有效期的id大于0  则需要计算商品的价格  id不大于0则代表永久有效 需要默认值
                original_price = course.price
                expire_text = "永久有效"

                try:
                    if expire_time > 0:
                        course_expire = CourseExpire.objects.get(course_id=course_id, expire_time=expire_time)
                        # 对应有效期的价格
                        original_price = course_expire.price
                        expire_text = course_expire.expire_text
                except CourseExpire.DoesNotExist:
                    pass

                # 根据已勾选的商品的对应有效期的价格去计算勾选商品的最终价格
                real_expire_price = course.real_expire_price(expire_time)

                # 将购物车所需的信息返回
                data.append({
                    "course_img": f'{HOST}{course.course_img.url}',
                    "name": course.name,
                    "id": course.id,
                    "expire_text": expire_text,
                    # 活动、有效期计算完成后的  真实价格
                    "real_price": float(f'{real_expire_price:.2f}'),
                    # 原价
                    "price": float(f'{original_price:.2f}'),
                    "discount_name": course.discount_name,
                })

                # 商品叠加后的总价
                total_price += real_expire_price

        return Response({"course_list": data, "total_price": total_price, "message": '获取成功'})

    def get_course_by_id(self, request, *args, **kwargs):
        course_id = kwargs.get('id')
        course = Course.objects.get(is_show=True, is_delete=False, pk=course_id)
        real_expire_price = course.real_expire_price(0)
        data = {
            "course_img": f'{HOST}{course.course_img.url}',
            "name": course.name,
            "id": course.id,
            "expire_text": "永久有效",
            "real_price": float(f'{real_expire_price:.2f}'),
            "price": float(f'{course.price:.2f}'),
            "discount_name": course.discount_name,
        }

        return Response(data)
