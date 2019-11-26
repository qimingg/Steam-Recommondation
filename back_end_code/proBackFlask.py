from flask import Flask
from flask import jsonify
from tasks import *
app = Flask(__name__)


@app.route("/test/", methods=['GET'])
def info():
    return "hello World"


@app.route("/names/", methods=['GET'])
def get_names():
    conn = get_connection()
    if conn is not None:
        res = select_names_10(conn)
        conn.close()
        return jsonify({'data': res})


if __name__ == "__main__":
    app.run(host='0.0.0.0',port = 50009)
