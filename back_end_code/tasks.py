import cx_Oracle
import traceback
from config import *

def get_connection():
    try:
        conn = cx_Oracle.connect(
            USER, PASSWORD, HOST + '/' + DATABASE, encoding="UTF-8"
        )  # 连接数据库
        print("--Oracle Database Connected.--")
        return conn
    except Exception:
        print(traceback.format_exc())
        print("[ERROR] Oracle DB not connected.")
        return None


def select_names_10(conn):
    cur = conn.cursor()  # 获取cursor
    sql = "select name from steam_games where rownum<=10"
    x = cur.execute(sql)
    res = x.fetchall()
    print('result of fetch:', res)
    cur.close()
    return res
