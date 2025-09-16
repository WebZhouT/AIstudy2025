import os

 # 获取项目根路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
 # 配置主数据库
DATABASE = {
    'ENGINE': 'mysql+pymysql',
    'URI': 'root:123456@localhost:3306/aichat',
    # MySQL的用户：root, 密码:root, 端口：3306,数据库：doubandata
    'ECHO': False
}

