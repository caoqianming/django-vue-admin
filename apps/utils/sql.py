from django.db import connection

def execute_raw_sql(sql: str, params=None):
    """执行原始sql并返回rows, columns数据

    Args:
        sql (str): 查询语句
        params (_type_, optional): 参数列表. Defaults to None.
    """
    with connection.cursor() as cursor:
        cursor.execute("SET statement_timeout TO %s;", [30000])
        if params:
            cursor.execute(sql, params=params)
        else:
            cursor.execute(sql)
        columns  = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        return columns, rows
    
def format_sqldata(columns, rows):
    return [columns] + rows, [dict(zip(columns, row)) for row in rows]


def query_all_dict(sql, params=None):
    '''
    查询所有结果返回字典类型数据
    :param sql:
    :param params:
    :return:
    '''
    with connection.cursor() as cursor:
        if params:
            cursor.execute(sql, params=params)
        else:
            cursor.execute(sql)
        columns  = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def query_one_dict(sql, params=None):
    """
    查询一个结果返回字典类型数据
    :param sql:
    :param params:
    :return:
    """
    with connection.cursor() as cursor:
        if params:
            cursor.execute(sql, params=params)
        else:
            cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        return dict(zip(columns, row))
    
import pymysql

class DbConnection:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.close()