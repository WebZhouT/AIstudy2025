import mysql.connector
from dbutils.persistent_db import PersistentDB
from flask import jsonify
from sqlalchemy.dialects.mysql import pymysql

from .config import DATABASE
from mysql.connector import errorcode


# 调用 pymysql.connect 方法创建数据库连接池
# pool = PersistentDB(
#     creator=pymysql,
#     maxusage=1000,
#     setsession=[
#         'SET AUTOCOMMIT = 1',
#         'SET time_zone = "+00:00"'
#     ],
#     host='127.0.0.1',  # 主机IP
#     user='root',  # 登录用户
#     password='123456',  # 密码
#     database='0104case1',  # 数据库名字
#     cursorclass=pymysql.cursors.DictCursor
# )
def connect_database():
    try:
        # 连接 MySQL 数据库
        connection = mysql.connector.connect(
            host=DATABASE['URI'].split('@')[1].split(':')[0],
            user=DATABASE['URI'].split(':')[0],
            password=DATABASE['URI'].split(':')[1].split('@')[0],
            database=DATABASE['URI'].split('/')[1]
        )
        return connection, None
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return None, {"code": 401, "data": None, "message": "账号或密码错误"}
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            return None, {"code": 401, "data": None, "message": "数据库不存在"}
        else:
            error_message = str(err)
            return None, {"code": 401, "data": None, "message": error_message}


# 关闭连接
async def close_connection(connection):
    connection.close()
