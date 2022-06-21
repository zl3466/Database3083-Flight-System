from crypt import methods
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors, hashlib
from datetime import timedelta
from datetime import datetime

app = Flask(__name__)
app.secret_key = '12345'
# establishing database connection 
connection = pymysql.connect(host = 'localhost',
                             user = 'root',
                             password = 'root',
                             db = 'flightsystem',
                             charset = 'utf8mb4',
                             port = 8889,
                             cursorclass = pymysql.cursors.DictCursor)
# main route
@app.route('/')
def index():
    return render_template('index.html')

# login route
@app.route('/login')
def login():
    return render_template('login.html')

# register route
@app.route('/register')
def register():
    return render_template('register.html')

# customer register route
@app.route('/cust_register')
def custRegister():
    return render_template('cust_register.html')

# staff register route
@app.route('/staff_register')
def staffRegister():
    return render_template('staff_register.html')

# customer login route
@app.route('/cust_login')
def custLogin():
    return render_template('cust_login.html')

# staff login route
@app.route('/staff_login')
def staffLogin():
    return render_template('staff_login.html')

# customer registration authentication route
# note: pattern similar to staff_registerAuth
@app.route('/cust_registerAuth', methods=['POST'])
def cust_registerAuth():
    # requesting registration info from forms using POST
    email = request.form['email']
    password = request.form['password']
    # hashing passwrod with md5
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    cursor = connection.cursor()
    # query to get data on registering user
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, (email))
    data = cursor.fetchone()

    error = None
    # case: user data in database --> throw error
    if(data):
        error = "This user already exists"
        return render_template('cust_register.html', error = error)
    else:
    # case: user data not in database --> insert new user data
        ins = 'INSERT INTO customer(email, password) VALUES(%s, %s)'
        cursor.execute(ins, (email, password))
        connection.commit()
        cursor.close()
        return render_template('index.html')

# staff registration authentication route 
# note: pattern similar to cust_registerAuth
@app.route('/staff_registerAuth', methods = ['POST'])
def staff_registerAuth():
    username = request.form['username']
    password = request.form['password']
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    cursor = connection.cursor()
    query = 'SELECT * FROM staff WHERE username = %s'
    cursor.execute(query, (username))
    data = cursor.fetchone()

    error = None
    if(data):
        error = "This user already exists"
        return render_template('staff_register.html', error = error)
    else:
        ins = 'INSERT INTO staff(username, password) VALUES(%s, %s)'
        cursor.execute(ins, (username, password))
        connection.commit()
        cursor.close()
        return render_template('index.html')

# customer login authentication route
# note: similar to staff_loginAuth
@app.route('/cust_loginAuth', methods=['POST'])
def cust_loginAuth():
    #
    email = request.form['email']
    password = request.form['password']
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    cursor = connection.cursor()
    # query to get password from login ingo
    query = 'SELECT password FROM customer where email = %s'
    cursor.execute(query, (email))
    data = cursor.fetchone()
    cursor.close()
    error = None
    if(data):
        # checking password
        if data['password'] == password:
            # setting session to current user
            session['email'] = email
            return redirect(url_for('cust_home'))
        # case: password does not match --> throw error
        else:
            error = "Incorrect password"
            return render_template('cust_login.html', error = error)
    # case: email does not exist --> throw error
    else:
        error = "Invalid email"
        return render_template('cust_login.html', error = error)

# staff login authentication route
# note: similar to cust_loginAuth
@app.route('/staff_loginAuth', methods=['POST'])
def staff_loginAuth():
    username = request.form['username']
    password = request.form['password']
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    cursor = connection.cursor()
    query = 'SELECT password FROM staff where username = %s'
    cursor.execute(query, (username))
    data = cursor.fetchone()
    cursor.close()
    error = None
    if(data):
        if data['password'] == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            error = "Incorrect password"
            return render_template('staff_login.html', error = error)
    else:
        error = "Invalid username"
        return render_template('staff_login.html', error = error)

# customer homepage route
@app.route('/cust_home')
def custHome():
    return render_template('cust_home.html')

# public information route
@app.route('/publicinfo')
def publicinfo():
    return render_template('publicinfo.html')

# view flights(public) route
@app.route('/public_viewflights')
def public_viewFlights():
    # declaring timestamp for now
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours = 2)
    valid_time = valid_timestamp.time()
    valid_date = valid_timestamp.date()
    cursor = connection.cursor()
    # query to get all upcoming flight data
    query = 'SELECT * FROM flight WHERE (departure_date>%s) OR (departure_date=%s and departure_time>%s)'
    cursor.execute(query, (valid_date, valid_date, valid_time))
    data = cursor.fetchall()
    cursor.close()
    # parsing through each flight to get search parameters \
    # and storing 
    for each in data:
        src_port = each['src_name']
    return render_template('public_viewflights.html', data = None)

@app.route('/public_flightsearch', methods = ['GET','POST'])
def public_flightSearch():
    param_dict={}
    param_dict['src_name'] = request.form['src_name']
    param_dict['dst_name'] = request.form['dst_name']
    param_dict['departure_date'] = request.form['departure_date']
    param_dict['departure_time'] = request.form['departure_time']
    # dst_name = request.form['dst_name']
    # departure_date = request.form['departure_date']
    # departure_time = request.form['departure_time']
    # param_list = []
    query = "SELECT * FROM flight"
    search_string = ""
    param_keys = []
    param_values = []
    for items in param_dict:
        if len(param_dict[items])>1:
            param_keys.append(items)
    if len(param_keys)>0:
        search_string = " WHERE {} = %s".format(param_keys[0])
        param_values.append(param_dict[param_keys[0]])
    if len(param_keys)>1:
        for items in param_keys[1:]:
            search_string += " and {} = %s".format(items)
            param_values.append(param_dict[items])
    param_tuple = tuple(param_values)
    search = query + search_string
    cursor = connection.cursor()
    cursor.execute(search, param_tuple)
    data = cursor.fetchall()
    cursor.close()
    return render_template('public_viewflights.html',data=search, where=data)

@app.route('/public_viewflightsRT', methods=["POST"])
def public_viewflightsRT():
    return render_template('login.html')

if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)