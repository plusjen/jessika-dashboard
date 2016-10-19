import os

from functools import wraps
from flask import Flask, request, jsonify, render_template
from dotenv import Dotenv

env = None

try:
    env = Dotenv('./.env')
    client_id = env["AUTH0_CLIENT_ID"]
    client_secret = env["AUTH0_CLIENT_SECRET"]
except IOError:
  env = os.environ

app = Flask(__name__)



# Controllers API
@app.route("/ping")
def ping():
    return render_template('login.html')

if __name__ == "__main__":
    #app.run(host='0.0.0.0', port = int(os.environ.get('PORT', 3080)))
    app.run(debug=True, port=80)
