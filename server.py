import os

from functools import wraps
from flask import Flask, request, jsonify, render_template
from dotenv import Dotenv

env = None

try:
    env = Dotenv('./.env')
except IOError:
    env = os.environ
  
client_id     = env["AUTH0_CLIENT_ID"]
client_secret = env["AUTH0_CLIENT_SECRET"]
namespace     = env["AUTH0_NAMESPACE"]  

app = Flask(__name__)


@app.route("/callback")
def callback():
    return "Login successfull"


# Controllers API
@app.route("/")
def ping():
    return render_template('login.html', client_id=client_id, namespace=namespace)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port = int(os.environ.get('PORT', 3080)))
    #app.run(debug=True, port=3080)
