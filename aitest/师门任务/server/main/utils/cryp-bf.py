from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
# 测试
import binascii

# 密匙
SECRET_KEY = 'Fn3L7EDzjqWjcaY2'
key = SECRET_KEY[:16].encode('utf-8')
iv = SECRET_KEY[:16].encode('utf-8')


# 加密函数
def genpassword(password):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(pad(password.encode('utf-8'), AES.block_size))
    return encrypted_data.hex()


# 解密函数
def exportpassword(password):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(bytes.fromhex(password)), AES.block_size)
    return decrypted_data.decode('utf-8')


# 测试方法

# # 要解密的字符串
# ciphertext = "HZHR9Uho1wiocMdo3x8C3A=="
#
# # 调用解密函数进行解密
# decrypted_data = exportpassword(ciphertext)
#
# # 打印解密后的数据
# print("Decrypted Data:", decrypted_data)
