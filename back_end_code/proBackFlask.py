# -*- coding: utf-8 -*-
from flask import Flask
from flask import jsonify
from tasks import *
from flask import request
from flask_cors import CORS
import json

app = Flask(__name__)

CORS(app, resources=r'/api/*')


#--------------------------
#------- dashboard --------
#--------------------------

@app.route("/api/dashboard/top", methods=["GET"])
def get_top_ratings():
    tag = request.args.get('tag')
    if tag:
        tag = json.loads(tag)  # list of strings
    conn = get_connection()
    res = None
    if conn is not None:
        status = 'success'
        res = select_top_ratings(conn, tag)
        conn.close()
    else:
        status = 'failure'
    return jsonify({'data': res, 'DBstatus': status})


@app.route("/api/dashboard/search", methods=["GET"])
def dashboard_search():
    title = request.args.get('title', '', str).lower()
    limit = request.args.get('limit', '5')
    offset = request.args.get('offset', '0')
    if not title:
        return jsonify(dict(error='lack of parameters'))
    try:
        limit = int(limit)
        offset = int(offset)
    except ValueError:
        return jsonify(dict(error='parameters error'))
    conn = get_connection()
    res = None
    if conn is not None:
        status = 'success'
        res = search_games(conn, title, limit, offset)
        conn.close()
    else:
        status = 'failure'
    return jsonify({'data': res, 'DBstatus': status})


#--------------------------
#------- Game Page --------
#--------------------------


@app.route("/api/game", methods=["GET"])
def game():
    # check the request
    gameid = request.args.get('gameid', '', str)
    if not gameid:
        return jsonify(dict(error='lack of parameters'))
    try:
        gameid = int(gameid)
    except ValueError:
        return jsonify(dict(error='parameters error'))

    # check DB connection and execute query
    conn = get_connection()
    res = None
    if conn is not None:
        status = 'success'
        res = game_details(conn, gameid)
        conn.close()
    else:
        status = 'failure'
    return jsonify({'data': res, 'DBstatus': status})

#----------------
#--- wishList ---
#----------------

@app.route("/api/wishlist/add", methods=['POST'])
def wishlist_add_game():
    conn = get_connection()
    if conn is not None:
        status = 'success'
    else:
        status = 'failure'
    if request.method == 'POST':
        gameid = request.form['gameid']
        res = add_like(conn, gameid)
        print(gameid)
        res = gameid
        conn.close()
        return jsonify({'data': res, 'DBstatus': status})


@app.route("/api/wishlist/del", methods=['POST'])
def wishlist_delete_game():
    conn = get_connection()
    if conn is not None:
        status = 'success'
    else:
        status = 'failure'
    if request.method == 'POST':
        gameid = request.form['gameid']
        res = delete_like(conn, gameid)
        print(gameid)
        res = gameid
        conn.close()
        return jsonify({'data': res, 'DBstatus': status})


@app.route("/api/wishlist/show", methods=['GET'])
def wishlist_show_game():
    order = request.args.get('order')
    if order is None:
        order = 0
    else:
        try:
            order = int(order)
        except ValueError:
            return jsonify(dict(error='parameters error'))
    conn = get_connection()
    if conn is not None:
        status = 'success'
    else:
        status = 'failure'
    res = show_wishlist(conn, order)
    print(res)
    conn.close()
    return jsonify({'data': res, 'DBstatus': status})


@app.route("/api/wishlist/recommendation", methods=['GET'])
def wishlist_recommend():
    conn = get_connection()
    if conn is not None:
        status = 'success'
    else:
        status = 'failure'
    res = wishlist_rec(conn)
    print(res)
    conn.close()
    return jsonify({'data': res, 'DBstatus': status})


#------------
#--- test ---
#------------

@app.route("/api/test/", methods=['GET'])
def info():
    return "hello World"


@app.route("/api/names", methods=['GET'])
def get_names():
    conn = get_connection()
    res = None
    if conn is not None:
        status = 'success'
        res = select_names_10(conn)
        conn.close()
    else:
        status = 'failure'
    return jsonify({'data': res, 'DBstatus': status})


@app.route("/api/posttest", methods=['POST'])
def post_test():
    conn = get_connection()
    if conn is not None:
        status = 'success'
    else:
        status = 'failure'
    if request.method == 'POST':
        game_id = request.form['game_id']
        res = add_like(conn, game_id)
        print(game_id)
        res = game_id
        conn.close()
        return jsonify({'data': res, 'DBstatus': status})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
