# 生成token
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


def create_token(user):
    return jwt_encode_handler(jwt_payload_handler(user))
