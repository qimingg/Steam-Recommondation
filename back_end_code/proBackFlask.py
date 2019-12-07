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
#--- test ---
#--------------------------

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
    return jsonify({'data': res, 'status': status})


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
        return jsonify({'data': res, 'status': status})
#--------------------------
#--- dashboard ---
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
    return jsonify({'data': res, 'status': status})

@app.route("/api/dashboard/search", methods=["GET"])
def dashboard_search():
    title = request.args.get('title', '', str).lower()
    conn = get_connection()
    res = None
    if conn is not None:
        status = 'success'
        res = search_games(title)
        conn.close()
    else:
        status = 'failure'
    return jsonify({'data': res, 'status': status})



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=50009)
