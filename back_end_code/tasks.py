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


#####################
##### DASHBOARD #####
#####################
def select_top_ratings(conn, tag):
    '''
    A function that return top n games based on ratings.
    :param conn:
    :return: [(),(),..]
    #return (str:name, int:positive_ratings, str:tags, str:url of header_image) in order.
    '''
    cur = conn.cursor()
    # on dashboard
    if tag is not None and len(tag) != 0:
        if len(tag) == 1:
            pref = "WITH game_appid AS " \
                   "(SELECT steam_appid FROM steam_genres " \
                   "WHERE genres = '%s')"%tag[0]
        else:
            pref = "WITH game_appid AS(" + \
                   ' intersect '.join(["SELECT steam_appid FROM steam_genres WHERE genres = '%s'"%i for i in tag]) + \
                    ')'

        # get top 10 based on ratings
        sql = "SELECT * FROM " \
              "(SELECT g.appid, g.name, ROUND(g.positive_ratings / (g.positive_ratings + g.negative_ratings) * 10, 1) AS rating, g.tags, h.header_image " \
              "FROM steam_games g, steam_headerimage h, game_appid ga " \
              "WHERE g.appid = h.steam_appid " \
              "AND ga.steam_appid = g.appid " \
              "AND g.positive_ratings >= 1000 " \
              "ORDER BY rating DESC) " \
              "WHERE ROWNUM <= 10"
        # get top 10 based on numbers of views
        sql2 = "SELECT g.appid, t.title, t.num as num_of_reviews, g. tags, h.header_image " \
               "FROM " \
               "(SELECT * FROM " \
               "(SELECT title, COUNT(*) as num " \
               "FROM steam_reviews " \
               "GROUP BY title " \
               "ORDER BY COUNT(*) DESC) " \
               ") t, steam_games g, steam_headerimage h, game_appid ga " \
               "WHERE t.title = g.name " \
               "AND ga.steam_appid = g.appid " \
               "AND g.appid = h.steam_appid " \
               "ORDER BY num_of_reviews DESC"
        sql = pref + sql
        sql2 = pref + sql2

    # select with no tags
    else:
        sql = "WITH temp AS" \
              "(SELECT g.appid, g.name, ROUND(g.positive_ratings / (g.positive_ratings + g.negative_ratings) * 10, 1) AS rating, g.tags, h.header_image " \
              "FROM steam_games g, steam_headerimage h " \
              "WHERE g.appid = h.steam_appid " \
              "AND g.positive_ratings >= 1000 " \
              "ORDER BY rating DESC) " \
              "SELECT * FROM temp " \
              "WHERE ROWNUM <= 10"
        sql2 = "WITH temp AS " \
               "(SELECT * FROM" \
               "(SELECT title, COUNT(*) as num " \
               "FROM steam_reviews " \
               "GROUP BY title " \
               "ORDER BY COUNT(*) DESC) " \
               "WHERE ROWNUM <= 10) " \
               "SELECT g.appid, t.title, t.num as num_of_reviews, g. tags, h.header_image " \
               "FROM temp t, steam_games g, steam_headerimage h " \
               "WHERE t.title = g.name " \
               "AND g.appid = h.steam_appid " \
               "ORDER BY num_of_reviews DESC"
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

#####################
##### SEARCHING #####
#####################

def search_games(conn, title, limit, offset, price=None, tags=None):
    '''
    search for games in steam database
    :param title: str
    :param price: [0,20]
    :param tags: ['','']
    :return:
    '''
    cur = conn.cursor()
    # dashboard search
    if price is None and tags is None:
        sql = "SELECT appid, name, rating, tags, header_image FROM (" \
              "SELECT ROWNUM AS rn, g.appid, g.name, g.positive_ratings," \
              "ROUND(g.positive_ratings / (g.positive_ratings + g.negative_ratings) * 10, 1) AS rating, g.tags, h.header_image " \
              "FROM steam_games g, steam_headerimage h " \
              "WHERE LOWER(g.name) like '%%%s%%' AND g.appid = h.steam_appid " \
              "ORDER BY g.positive_ratings DESC) temp " \
              "WHERE temp.rn>%s AND temp.rn<=%s" % (title, offset, offset+limit)
        print(sql)
        try:
            x = cur.execute(sql)
            res = x.fetchall()
            print('result of fetch:', res)

        except Exception:
            print(traceback.format_exc())
            print("[ERROR] SQL query not executed.", sql)
            cur.close()
            return None
        cur.close()
        return res

    # searching with advanced filtering
    else:
        #TODO
        return [[]]

#####################
##### GAME PAGE #####
#####################

def game_details(conn, gameid):
    """
    Show game details in the game page
    :param gameid: int
    :return: list
    """
    cur = conn.cursor()
    try:
        sql = "SELECT * FROM steam_games WHERE appid = '%s'" % gameid
        x = cur.execute(sql)
        res = list(x.fetchone())
        res[5] = res[5].replace(';', '; ')
        sql = "SELECT short_description FROM steam_description WHERE steam_appid = '%s'" % gameid
        x = cur.execute(sql)
        lst = x.fetchone()
        if lst == None:
            lst = ['Not shown']
        res.extend(list(lst))
        sql = "SELECT header_image FROM steam_headerimage WHERE steam_appid = '%s'" % gameid
        x = cur.execute(sql)
        lst = x.fetchone()
        if lst == None:
            lst = ['']
        res.extend(list(lst))
        sql = "SELECT minimum,recommended FROM steam_requirements WHERE steam_appid = '%s'" % gameid
        x = cur.execute(sql)
        lst = x.fetchone()
        if lst == None:
            lst = ['Not shown', 'Not shown']
        res.extend(list(lst))
        sql = "SELECT thumbnail,full_image FROM steam_screenshots WHERE steam_appid = '%s' AND ROWNUM <= 3" % gameid
        x = cur.execute(sql)
        lst = x.fetchone()
        if lst == None:
            lst = ['']
        res.append(list(lst))
        print(res)
        cur.close()
        return res

    except Exception:
        print(traceback.format_exc())
        print("[ERROR] SQL query not executed.", sql)
        cur.close()
        return None

#####################
##### WISH-LIST #####
#####################

def add_like(conn, gameid):
    """
    delete a game which is already in the wish-list
    :param conn: connection
    :param gameid: int
    :return: bool
    """
    cur = conn.cursor()
    sql = "insert into usertable values('localhost','%s')" % gameid
    try:
        x = cur.execute(sql)
        print("insertion success.", sql)
        conn.commit()
        cur.close()
        return True
    except Exception:
        print(traceback.format_exc())
        print("[ERROR] SQL query not executed.",sql)
        cur.close()
        return False


def delete_like(conn, gameid):
    """
    delete a game which is already in the wish-list
    :param conn: connection
    :param gameid: int
    :return: bool
    """
    cur = conn.cursor()
    sql = "DELETE FROM usertable WHERE gameid='%s'" % gameid
    try:
        cur.execute(sql)
        print("deletion success.", sql)
        conn.commit()
        cur.close()
        return True
    except Exception:
        print(traceback.format_exc())
        print("[ERROR] SQL query not executed.")
        cur.close()
        return False


def show_wishlist(conn, order):
    """
    Show every game and its information in the waitlist on the page
    :param conn:
    :param order: int
    :return:
    """
    cur = conn.cursor()
    sql = "SELECT g.appid, g.name, " \
          "ROUND(g.positive_ratings / (g.positive_ratings + g.negative_ratings) * 10, 1) AS rating," \
          "g.tags, h.header_image, g.price " \
          "FROM usertable u, steam_games g, steam_headerimage h " \
          "WHERE u.gameid = g.appid AND g.appid = h.steam_appid " \
          "ORDER BY "
    if order == 0:
        sql += "g.name"
    elif order == 1:
        sql += "g.name DESC"
    elif order == 2:
        sql += "g.price"
    elif order == 3:
        sql += "g.price DESC"

    try:
        x = cur.execute(sql)
        res = x.fetchall()
        cur.close()
        return res
    except Exception:
        print(traceback.format_exc())
        print("[ERROR] SQL query not executed.")
        cur.close()
        return None


def wishlist_rec(conn):
    """
    show recommendations of wishlist
    :param conn:
    :return:
    """
    cur = conn.cursor()
    sql = "WITH f AS(SELECT t.price, sg.genres FROM (" \
          "SELECT g.appid, g.name, g.price FROM usertable u, steam_games g WHERE u.gameid = g.appid) t " \
          "LEFT JOIN steam_genres sg ON t.appid = sg.steam_appid)," \
          "genres AS(SELECT genres AS genre, rownum AS rn FROM (" \
          "SELECT genres, COUNT(*) AS c FROM f GROUP BY genres ORDER BY c DESC )" \
          "WHERE ROWNUM <= 2)" \
          "(SELECT * from (" \
          "SELECT g.appid, g.name, g.price, g.tags, h.header_image " \
          "FROM steam_games g, steam_genres ge, steam_headerimage h " \
          "WHERE g.appid = ge.steam_appid AND g.appid = h.steam_appid " \
          "AND g.appid not in (SELECT gameid FROM usertable)AND g.price <= (SELECT MAX(price) FROM f)" \
          " AND g.price >= (SELECT MIN(price) FROM f) AND ge.genres = (SELECT genre FROM genres WHERE rn = 1)" \
          "ORDER BY g.average_playtime)WHERE ROWNUM <= 5)" \
          "UNION (SELECT * from (SELECT g.appid, g.name, g.price, g.tags, " \
          "h.header_image FROM steam_games g, steam_genres ge, steam_headerimage h " \
          "WHERE g.appid = ge.steam_appid AND g.appid = h.steam_appid " \
          "AND g.appid not in (SELECT gameid FROM usertable)" \
          "AND g.price <= (SELECT MAX(price) FROM f)" \
          "AND g.price >= (SELECT MIN(price) FROM f)" \
          "AND ge.genres = (SELECT genre FROM genres WHERE rn = 2)" \
          "ORDER BY g.average_playtime)WHERE ROWNUM <= 3)"
    try:
        x = cur.execute(sql)
        res = x.fetchall()
        cur.close()
        return res
    except Exception:
        print(traceback.format_exc())
        print("[ERROR] SQL query not executed.")
        cur.close()
        return None





if __name__ == "__main__":
    conn = get_connection()

    conn.close()