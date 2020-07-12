import requests
from edu_api.settings.constans import SINGLE_SEND_URL, API_KEY


class Message:

    def __init__(self, api_key):
        self.api_key = api_key
        self.single_send_url = SINGLE_SEND_URL

    def send_message(self, phone, code):
        params = {
            'apikey': self.api_key,
            'mobile': phone,
            'text': "【毛信宇test】您的验证码是{code}。如非本人操作，请忽略本短信".format(code=code)
        }
        res = requests.post(self.single_send_url, data=params)
        print(res)
        return res
