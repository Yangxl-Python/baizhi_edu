import re

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status as http_status
from rest_framework.viewsets import ViewSet

from edu_api.libs.geetest import GeetestLib
from edu_api.settings.constans import MATCH_PHONE, SMS_EXPIRE_TIME, PHONE_EXPIRE_TIME, API_KEY
from user.models import UserInfo
from user.serializer import UserModelSerializer
from user.utils import get_user_by_account
from edu_api.utils.get_random_code import get_random_code
from edu_api.utils.create_token import create_token
# from edu_api.utils.send_msg import Message

from django_redis import get_redis_connection


pc_geetest_id = "6f91b3d2afe94ed29da03c14988fb4ef"
pc_geetest_key = "7a01b1933685931ef5eaf5dabefd3df2"


class CaptchaAPIView(APIView):
    """极验验证码"""

    user_id = 0
    status = False

    def get(self, request, *args, **kwargs):
        """获取验证码"""

        username = request.query_params.get('username')
        user = get_user_by_account(username)
        if user is None:
            return Response({"message": "用户不存在"}, status=http_status.HTTP_400_BAD_REQUEST)

        self.user_id = user.id

        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        self.status = gt.pre_process(self.user_id)
        response_str = gt.get_response_str()
        return Response(response_str)

    def post(self, request, *args, **kwargs):
        """验证验证码"""
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        # 判断用户是否存在
        if self.user_id:
            result = gt.success_validate(challenge, validate, seccode, self.user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        result = {"status": "success"} if result else {"status": "fail"}
        return Response(result)


class UserRegisterAPIView(CreateAPIView):
    serializer_class = UserModelSerializer
    queryset = UserInfo.objects.all()


class CheckPhoneAPIView(APIView):

    def get(self, request, *args, **kwargs):
        number = kwargs.get('number')
        if not re.match(MATCH_PHONE, number):
            return Response({'message': '手机号格式错误'}, status=http_status.HTTP_400_BAD_REQUEST)

        if get_user_by_account(number) is not None:
            return Response({'message': '手机号已被注册'}, status=http_status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'ok'})


class SendMessageAPIView(APIView):

    def get(self, request, number):
        redis_connection = get_redis_connection('sms_code')  # 获取Redis连接
        sms_key = f'sms_{number}'  # 根据手机号设置发送间隔的key
        phone_key = f'phone_{number}'  # 根据手机号保存对应验证码的key

        if redis_connection.get(sms_key):
            return Response({'message': f'您已经在{SMS_EXPIRE_TIME}s内发送过短信了~'}, status=http_status.HTTP_400_BAD_REQUEST)

        code = '%06d' % get_random_code()

        redis_connection.setex(sms_key, SMS_EXPIRE_TIME, code)  # 设置验证码发送间隔，SMS_EXPIRE_TIME后可再次发送
        redis_connection.setex(phone_key, PHONE_EXPIRE_TIME, code)  # 设置验证码，PHONE_EXPIRE_TIME后过期

        try:
            # 通过celery异步执行发送短信的服务
            from my_task.sms.tasks import send_sms
            # 调用任务函数  发布任务
            send_sms.delay(number, code)  # 如果需要参数则传递过去 不需要则不传递
            # message = Message(API_KEY)
            # message.send_message(number, code)
        except:
            return Response({'message': '短信发送失败'}, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': '发送短信成功'})


class PhoneLoginViewSet(ViewSet):

    def login(self, request, *args, **kwargs):
        UserModelSerializer().validate(request.data)  # 验证手机号与验证码是否匹配
        user = UserInfo.objects.filter(phone=request.data.get('phone')).first()  # 获取用户
        user.token = create_token(user)  # 生成token
        return Response(UserModelSerializer(user).data)
