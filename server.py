import os
import json

import tempfile
import calendar
import requests
import urlparse
import psycopg2
import psycopg2.extras
from functools import wraps
from datetime import date, datetime, timedelta
from flask import Flask, request, session, redirect, render_template, send_from_directory
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

# temporary
user_data = {
        'labels': ["Oct1", "Oct4", "Oct7", "Oct10", "Oct13", "Oct16", "Oct19", "Oct22", "Oct25", "Oct28",  "Oct31"],
        'axis0' : [203,156,99,251,305,247, 300, 260, 210, 270, 200],
        'axis1' : [303,196,28,201,150,120, 200, 230, 260, 230, 200],
        
        'trr': '$250.00',
        'tcr': 59,
        'tc' : 92,
        'art': '34 sec'
    }
    
# # # # # # # # # # # # # # # # # # # # # # # # # # #    

def get_week(thedate):
    """
    Return the full week (Sunday first) of 
    the week containing the given date.
    """
    # turn sunday into 0, monday into 1, etc.
    day_idx = (thedate.weekday() + 1) % 7  
    sunday = thedate - timedelta(days=day_idx)
    theweek = [sunday + timedelta(days=n) for n in range(7)]
    return theweek
  
  
def get_month(thedate):
    year, month = thedate.year, thedate.month
    num_days = calendar.monthrange(year, month)[1]
    days = [date(year, month, day) for day in range(1, num_days+1)]
    return days
    

def get_quarter(thedate):
    year = thedate.year
    days = []
    for k in range(1, 4 + 1):
        month = 4 * ((thedate.month - 1) / 4) + k
        num_days = calendar.monthrange(year, month)[1]
        for day in range(1, num_days+1):
            days.append( date(year, month, day) )
    return days  
    
def get_year(thedate):
    this_year = thedate.year
    next_year = thedate.year + 1
    delta = date(next_year, 1, 1) - date(this_year, 1, 1)
    days = [date(this_year, 1, 1) + timedelta(days=n) for n in range(delta.days + 1)]        
    return days

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

    cur = conn.cursor()
    
    user_id = session['profile']['user_id']
    query = '''SELECT client_id FROM dashboard_users WHERE user_id = %s '''
    cur.execute(query, (user_id, ))
    response = cur.fetchone()
    
    if response:
        
        client = response[0]
        query = '''SELECT view_client_id FROM dashboard_permissions WHERE client_id = %s ORDER BY 1'''
        cur.execute(query, (client, ))
        response = cur.fetchall()
        clients = [item[0] for item in response]
        
        client_id = clients[0]
        params  = {'client_id': client_id, }
        names   = ['trr', 'tcr', 'tc']
        formatters = ["${:.2f}", "{}", "{}"]
        queries = ['''SELECT amount FROM processed_payments WHERE consumer_id = %(client_id)s''', 
                   '''SELECT COUNT(DISTINCT from_phonenumber) FROM outgoingmessages 
                             JOIN consumers ON consumers.phonenumber = outgoingmessages.phonenumber
                             WHERE client_id = %(client_id)s''',
                   '''SELECT COUNT(DISTINCT to_phonenumber) FROM incomingmessages 
                             JOIN consumers ON consumers.phonenumber = incomingmessages.phonenumber
                             WHERE client_id = %(client_id)s'''] 
        
        for name, query, formatter in zip(names, queries, formatters):
            cur.execute(query, params)
            response = cur.fetchone()
            user_data[name] = formatter.format(response[0] if response else 0)
        
            
        query = '''SELECT thedate, COUNT(DISTINCT message) FROM (
                       SELECT DATE(outgoingmessages.timestamp) AS thedate, 
                              messageid AS message
                       FROM outgoingmessages 
                       JOIN consumers ON consumers.phonenumber = outgoingmessages.phonenumber
                       WHERE client_id = %(client_id)s
                       
                       UNION ALL
                       
                       SELECT DATE(incomingmessages.timestamp) AS thedate, 
                              messageid AS message
                       FROM incomingmessages 
                       JOIN consumers ON consumers.phonenumber = incomingmessages.phonenumber
                       WHERE client_id = %(client_id)s
                   ) t
                   GROUP BY 1 ORDER BY 1'''
        cur.execute(query, params)
        messages = cur.fetchall()
        
        query = '''SELECT DATE(incomingmessages.timestamp), 
                          COUNT(DISTINCT incomingmessages.phonenumber)
                   FROM incomingmessages 
                   JOIN consumers ON consumers.phonenumber = incomingmessages.phonenumber
                   WHERE client_id = %(client_id)s
                   GROUP BY 1 ORDER BY 1'''
        cur.execute(query, params)
        conversations = cur.fetchall()
        
        
        
        now = datetime.now().date()
        items = ['this week', 'last week', 'this month', 'last month', 'this quater', 'this year']
        dates = [now, 
                 now - timedelta(days=7), 
                 now, 
                 now - timedelta(days=calendar.monthrange(now.year, now.month)[1]), 
                 now, 
                 now] 
        generators = [get_week, get_week, get_month, get_month, get_quarter, get_year]
        formatters = ["%a", "%a", "%b %d", "%b %d", "%b %d", "%m %d"]
        
        conv = {x: y for x, y in conversations}
        mesg = {x: y for x, y in messages}
        
        for item, thedate, func, fmt in zip(items, dates, generators, formatters):
            the_range = func(thedate)
            labels = [day.strftime(fmt) for day in the_range]
            axis0  = [int(conv.get(day, 0)) for day in the_range]
            axis1  = [int(mesg.get(day, 0)) for day in the_range]
            user_data[item] = {'labels': labels, 'axis0': axis0, 'axis1': axis1}
        
        handler, json_tmp = tempfile.mkstemp(suffix='.json', prefix='user_data_', dir='public')
        with open(json_tmp, 'w') as fp:
            json.dump(user_data, fp)
        
        session['user-data-json'] = json_tmp.split('/', 2)[2]
        user_data['json_file'] = json_tmp.split('/', 2)[2]
        
        return render_template('dashboard.html', user=session['profile'], user_data=user_data)
    else:
        return render_template('failure.html')


@app.route('/logout')
def logout():
    # remove tmp json file with user's data
    if os.path.exists(session['user-data-json']):
        os.remove(session['user-data-json'])
    session.pop('user-data-json', None)
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
    
    
