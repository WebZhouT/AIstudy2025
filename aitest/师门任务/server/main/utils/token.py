import jwt
from datetime import datetime, timedelta

# 设定一个密钥，用来加密和解密token
token_key = 'XfZEpWEn?ARD7rHBN'
# 设定默认Token过期时间，单位秒
TOKEN_EXPIRE_SECOND = 3600

class Token:
    @staticmethod
    def encrypt(data):
        payload = {
            'userdata': data,
            'exp': datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRE_SECOND)
        }
        token = jwt.encode(payload, token_key, algorithm='HS256')
        return token

    @staticmethod
    def decrypt(token):
        try:
            data = jwt.decode(token, token_key, algorithms=['HS256'])
            return {
                'token': True,
                'data': data
            }
        except jwt.ExpiredSignatureError:
            return {
                'token': False,
                'data': 'Token已过期'
            }
        except jwt.InvalidTokenError:
            return {
                'token': False,
                'data': '无效的Token'
            }
