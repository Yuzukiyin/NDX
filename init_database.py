'''初始化数据库的模块 建库'''
#bought.sql
#生成fund.db

import sqlite3

class InitDatabase:
    def __init__(self, db_path='fund.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        with open('bought.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
            cursor.executescript(sql_script)
        
        conn.commit()
        conn.close()


# 向后兼容的函数接口
def init_database(db_path='fund.db'):
    """初始化数据库
    
    Args:
        db_path: 数据库路径
    """
    InitDatabase(db_path=db_path)


