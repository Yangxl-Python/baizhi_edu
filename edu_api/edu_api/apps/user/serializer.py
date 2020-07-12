import re

from django.contrib.auth.hashers import make_password
from django_redis import get_redis_connection
from rest_framework import serializers

from edu_api.settings.constans import MATCH_PHONE
from user.models import UserInfo
from user.utils import get_user_by_account

from utils.create_token import create_token


class UserModelSerializer(serializers.ModelSerializer):
    token = serializers.CharField(read_only=True, help_text='用户token')
    code = serializers.CharField(min_length=4, max_length=6, required=True, write_only=True, help_text='短信验证码')
    login = serializers.BooleanField(default=0, write_only=True, help_text='登录操作')

    class Meta:
        model = UserInfo
        fields = ('id', 'username', 'password', 'phone', 'token', 'code', 'login')

        extra_kwargs = {
            'id': {
                'read_only': True
            },
            'username': {
                'read_only': True
            },
            'password': {
                'write_only': True
            },
            'phone': {
                'write_only': True
            }
        }

    def validate(self, attrs):
        phone = attrs.get('phone')
        # password = attrs.get('password')  # 可用作密码格式验证
        code = attrs.get('code')

        # 验证手机号格式
        if not re.match(MATCH_PHONE, phone):
            raise serializers.ValidationError('手机号格式错误')

        # 验证是否是登录操作
        if not attrs.get('login'):
            # 验证手机号是否被注册
            user = get_user_by_account(phone)
            if user:
                raise serializers.ValidationError('当前手机号已被注册')

        # 验证手机号短信验证码是否正确
        redis_connection = get_redis_connection('sms_code')
        phone_key = f'phone_{phone}'
        phone_code = redis_connection.get(phone_key)
        if not phone_code:
            raise serializers.ValidationError('验证码已过期')
        elif phone_code.decode() != code:
            raise serializers.ValidationError('验证码不一致')
        else:
            # 成功后将验证码删除
            redis_connection.delete(phone_key)

        return attrs

    def create(self, validated_data):
        pwd = validated_data.get('password')
        hashed_pwd = make_password(pwd)
        phone = validated_data.get('phone')

        user = UserInfo.objects.create(username=phone, password=hashed_pwd, phone=phone)

        # 生成token
        user.token = create_token(user)

        return user
