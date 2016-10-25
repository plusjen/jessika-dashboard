import os
import json

import requests
import urlparse
import psycopg2
import psycopg2.extras
from functools import wraps
from flask import Flask, request, jsonify, session, redirect, render_template, send_from_directory
from dotenv import Dotenv


# # # # # # # # # # # # # # # # # # # # # # # # # # #
# Load Env variables
env = None

try:
  env = Dotenv('./.env')
except IOError:
  env = os.environ


# # # # # # # # # # # # # # # # # # # # # # # # # # #

app = Flask(__name__, static_url_path= '')
app.secret_key = 'wIJrsS92Hz16BwyRJiYG7p9N1ekdDj22'
app.debug = True

# # # # # # # # # # # # # # # # # # # # # # # # # # #

# database connection
urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])
conn = psycopg2.connect(
   database=url.path[1:],
   user=url.username,
   password=url.password,
   host=url.hostname,
   port=url.port
)

# # # # # # # # # # # # # # # # # # # # # # # # # # #


def fetch_data(conn, query, params):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute(query, params)
    data = cur.fetchall()
    
    return data


# # # # # # # # # # # # # # # # # # # # # # # # # # #

# Requires authentication annotation
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'profile' not in session:
            return redirect('/')
        return f(*args, **kwargs)

    return decorated


@app.route('/public/<path:filename>')
def static_files(filename):
    return send_from_directory('./public', filename)


# Controllers API
@app.route("/")
def home():
    return render_template('home.html', env=env)


@app.route("/dashboard")
@requires_auth
def dashboard():

    user_data = {
        'labels': ["Oct1", "Oct4", "Oct7", "Oct10", "Oct13", "Oct16", "Oct19", "Oct22", "Oct25", "Oct28",  "Oct31"],
        'axis0' : [203,156,99,251,305,247, 300, 260, 210, 270, 200],
        'axis1' : [303,196,28,201,150,120, 200, 230, 260, 230, 200],
        
        'trr': '$250.00',
        'tcr': 59,
        'tc' : 92,
        'art': '34 sec'
    }
    
    
    query = '''SELECT client_id FROM dashboard_users WHERE user_id = %s '''
    user_id = session['profile']['user_id']
    
    response = fetch_data(conn, query, (user_id, ))
    if response:
        
        client_id = response[0]['client_id']
    
        queries = ['SELECT amount FROM processed_payments WHERE consumer_id = %s', 
                   'SELECT COUNT(DISTINCT from_phonenumber) FROM consumers JOIN outgoingmessages ON phonenumber WHERE client_id = %s',
                   'SELECT COUNT(DISTINCT to_phonenumber) FROM consumers JOIN incomingmessages ON phonenumber WHERE client_id = %s', 
                   'SELECT amount FROM processed_payments WHERE consumer_id = %s'] # TODO
         
        for query in queries:
            data = fetch_data(conn, query, (client_id, ))[0]
            print(data)
        
        '''
        [['id'], ['firstname'], ['lastname'], ['phonenumber'], ['amount_owed'], 
         ['recurring_billing'], ['recurring_day'], ['timestamp'], ['client_id']
        ]
        [['messageid'], ['conversationid'], ['phonenumber'], ['message'], ['timestamp'], ['from_phonenumber']]
        [['messageid'], ['conversationid'], ['phonenumber'], ['message'], ['timestamp'], ['to_phonenumber']]
        [id | confirmation_id | consumer_id | amount | method |         timestamp]
        '''
    
        '''
        For revenue recovered:
            - just query the processed_payment table using the client_id
        For total customers reached:
            - query the consumers table using the client_id then do a join on outgoingmessages 
              using the consumers phonenumber.  the count unique # of consumers
        For total conversations:
            - Same as above but instead of joining on the outgoingmessages, 
              join on the incoming messages.  count unique
        For Average Response Time:
            - query the consumers table using the client_id, 
              then do a join on outgoingmessages and incomingmessage.  
              get the difference in timestamp. (incoming - outgoing) and compute the average
        '''
        
        return render_template('dashboard.html', user=session['profile'], user_data=user_data)
    else:
        return render_template('failure.html')


@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('profile', None)
    return redirect('/')


@app.route('/callback')
def callback_handling():
    code = request.args.get('code')

    json_header = {'content-type': 'application/json'}

    token_url = "https://{domain}/oauth/token".format(domain=env["AUTH0_DOMAIN"])
    token_payload = {
        'client_id'     : env['AUTH0_CLIENT_ID'],
        'client_secret' : env['AUTH0_CLIENT_SECRET'],
        'redirect_uri'  : env['AUTH0_CALLBACK_URL'],
        'code'          : code,
        'grant_type'    : 'authorization_code'
        }

    token_info = requests.post(token_url, data=json.dumps(token_payload), headers = json_header).json()

    user_url = "https://{domain}/userinfo?access_token={access_token}"  \
    .format(domain=env["AUTH0_DOMAIN"], access_token=token_info['access_token'])

    user_info = requests.get(user_url).json()

    session['profile'] = user_info

    return redirect('/dashboard')



if __name__ == "__main__":
    app.run(host='0.0.0.0', port = int(os.environ.get('PORT', 3000)))
    
    
