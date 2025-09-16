from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

# 密钥和IV
SECRET_KEY = b'Fn3L7EDzjqWjcaY2'
IV = SECRET_KEY[:16]


# 加密函数
def genpassword(password):
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, IV)
    encrypted_data = cipher.encrypt(pad(password.encode('utf-8'), AES.block_size))
    return base64.b64encode(encrypted_data).decode('utf-8')


# 解密函数
def exportpassword(encryptedpassword):
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, IV)
    decrypted_data = unpad(cipher.decrypt(base64.b64decode(encryptedpassword)), AES.block_size)
    return decrypted_data.decode('utf-8')


# 测试加密和解密
password = 'your_password'
encrypted_password = genpassword(password)
print("Encrypted Password:", encrypted_password)

decrypted_password = exportpassword(encrypted_password)
print("Decrypted Password:", decrypted_password)
