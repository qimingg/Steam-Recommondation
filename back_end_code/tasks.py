# -*- coding: utf-8 -*-
import cx_Oracle
import traceback
from config import *

def get_connection():
    try:
        conn = cx_Oracle.connect(
            USER, PASSWORD, HOST + '/' + DATABASE, encoding="UTF-8", nencoding = "UTF-8"
        )  # 连接数据库
        print("--Oracle Database Connected.--")
        return conn
    except Exception:
        print(traceback.format_exc())
        print("[ERROR] Oracle DB not connected.")
        return None


#################
##### TESTS #####
#################
def select_names_10(conn):
    cur = conn.cursor()  # 获取cursor
    sql = "select name from steam_games where rownum<=10"
    x = cur.execute(sql)
    res = x.fetchall()
    print('result of fetch:', res)
    cur.close()
    return res


def add_like(conn, game_id):
    cur = conn.cursor()
    sql = "insert into usertable values('localhost','%s')" % game_id
    try:
        x = cur.execute(sql)
        print("insertion success.", sql)
        conn.commit()
        cur.close()
        return True
    except Exception:
        print(traceback.format_exc())
        print("[ERROR] SQL query not executed.")
        cur.close()
        return None


#################
### DASHBOARD ###
#################
def select_top_ratings(conn, tag):
    '''
    A function that return top n games based on ratings.
    :param conn:
    :return: [(),(),..]
    #return (str:name, int:positive_ratings, str:tags, str:url of header_image) in order.
    '''
    cur = conn.cursor()
    # get top 10 based on ratings
    print(tag,type(tag))
    # on dashboard
    if tag:
        if len(tag) == 1:
            pref = "WITH game_appid AS\
                (SELECT steam_appid FROM steam_genres\
                WHERE genres = '%s')"%tag[0]
        else:
            pref = "WITH game_appid AS(" + \
                   ' intersect '.join(["SELECT steam_appid FROM steam_genres WHERE genres = '%s'"%i for i in tag]) + \
                    ')'

        sql = "SELECT * FROM\
                (SELECT g.name, ROUND(g.positive_ratings / (g.positive_ratings + g.negative_ratings) * 10, 1) AS rating, g.tags, h.header_image\
                FROM steam_games g, steam_headerimage h, game_appid ga\
                WHERE g.appid = h.steam_appid\
                AND ga.steam_appid = g.appid\
                AND g.positive_ratings >= 1000\
                ORDER BY rating DESC)\
                WHERE ROWNUM <= 10"
        # get top 10 based on numbers of views
        sql2 = "SELECT t.title, t.num as num_of_reviews, g. tags, h.header_image\
                FROM \
                (SELECT * FROM\
                (SELECT title, COUNT(*) as num\
                FROM steam_reviews\
                GROUP BY title\
                ORDER BY COUNT(*) DESC)\
                WHERE ROWNUM <= 10) t, steam_games g, steam_headerimage h, game_appid ga\
                WHERE t.title = g.name\
                AND ga.steam_appid = g.appid\
                AND g.appid = h.steam_appid\
                ORDER BY num_of_reviews DESC"
        sql = pref + sql
        sql2 = pref + sql2

    # select on tags
    else:
        sql = "WITH temp AS\
            (SELECT g.name, ROUND(g.positive_ratings / (g.positive_ratings + g.negative_ratings) * 10, 1) AS rating, g.tags, h.header_image\
            FROM steam_games g, steam_headerimage h\
            WHERE g.appid = h.steam_appid\
            AND g.positive_ratings >= 1000\
            ORDER BY rating DESC)\
            SELECT * FROM temp\
            WHERE ROWNUM <= 10"
        sql2 = "WITH temp AS\
            (SELECT * FROM\
            (SELECT title, COUNT(*) as num\
            FROM steam_reviews\
            GROUP BY title\
            ORDER BY COUNT(*) DESC)\
            WHERE ROWNUM <= 10)\
            SELECT t.title, t.num as num_of_reviews, g. tags, h.header_image\
            FROM temp t, steam_games g, steam_headerimage h\
            WHERE t.title = g.name\
            AND g.appid = h.steam_appid\
            ORDER BY num_of_reviews DESC"
    try:
        res = {}
        x = cur.execute(sql)
        res['ratings'] = x.fetchall()
        x = cur.execute(sql2)
        res['views'] = x.fetchall()
        print('result of fetch:', res)

    except Exception:
        print(traceback.format_exc())
        print("[ERROR] SQL query not executed.")
        cur.close()
        return None
    cur.close()
    return res


def search_games(title, price=None, tags=None):
    '''
    search for games in steam database
    :param title: str
    :param price: [0,20]
    :param tags: ['','']
    :return:
    '''
    # dashboard search
    if price is None and tags is None:
        sql = "select name from steam_games where lower(name) like '%%%s%%';"%title
        try:
            x = cur.execute(sql)
            res['ratings'] = x.fetchall()
            print('result of fetch:', res)

        except Exception:
            print(traceback.format_exc())
            print("[ERROR] SQL query not executed.")
            cur.close()
            return None
        cur.close()
        return res





if __name__ == "__main__":
    conn = get_connection()
    select_top_ratings(conn)
    conn.close()