from django.conf import settings
from urllib.parse import urlencode

class QQOauth(object):
    def get_oauth_url(self):

            # 确认请求的url
            base_url = 'https://graph.qq.com/oauth2.0/authorize?'
            state = 'test'
            # 确认请求的参数
            params = {
                'response_type': 'code',
                'client_id': settings.QQ_APP_ID,
                'redirect_uri': settings.QQ_REDIRECT_URL,
                'state': state
            }
            # 将参数拼接到url中
            # urlencode可以将字典 转变为 key=value 的形式
            auth_url = base_url + urlencode(params)
            return auth_url