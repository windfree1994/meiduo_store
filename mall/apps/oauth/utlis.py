from django.conf import settings
from urllib.parse import urlencode,parse_qs
from urllib.request import urlopen
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
    def get_access_token(self,code):
        # 准备url,注意添加?
        base_url = 'https://graph.qq.com/oauth2.0/token?'
        # 拼接参数
        params = {
            'grant_type': 'authorization_code',
            'clint_id': settings.QQ_APP_ID,
            'clint_secret': settings.QQ_APP_KEY,
            'code': code,
            'redirect_uri': settings.QQ_REDIRECT_URL
        }
        # 生成URL
        token_url = base_url + urlencode(params)
        # 发送请求获取返回数据
        response = urlopen(token_url)
        # response可以用read来读取 但是它是Bytes类型
        data = response.read().decode()
        # 将qs 查询字符串格式数据转换为python字典
        from urllib.parse import parse_qs
        res_params = parse_qs(data)
        access_token = res_params['access_token']
        access_token = access_token[0]
        return access_token