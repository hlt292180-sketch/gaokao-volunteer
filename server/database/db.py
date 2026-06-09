# 数据库连接工具 —— 获取 pymysql 连接
# 使用参数化查询防止 SQL 注入：cursor.execute(sql, (param1, param2))

import pymysql
import sys
import os

# 确保能 import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def get_conn():
    """返回一个 MySQL 连接"""
    return pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset=Config.DB_CHARSET,
        cursorclass=pymysql.cursors.DictCursor  # 返回字典而非元组
    )
