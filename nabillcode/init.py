from crypt import methods
from os import times
from sqlite3 import connect
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

# ---------------------------------MAIN-------------------------------------------

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

# ---------------------------------REGISTER-------------------------------------------

# customer register route
@app.route('/customer_register')
def customer_register():
    return render_template('customer_register.html')

# staff register route
@app.route('/staff_register')
def staff_register():
    return render_template('staff_register.html')


# customer registration authentication route
# note: pattern similar to staff_registerAuth
@app.route('/customer_registerAuth', methods=['POST'])
def customer_registerAuth():
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
        cursor.close()
        return render_template('customer_register.html', error = error)
    
    # case: user data not in database --> insert new user data
    else:
        session['email'] = email
        ins = 'INSERT INTO customer(email, password) VALUES(%s, %s)'
        cursor.execute(ins, (email, password))
        connection.commit()
        cursor.close()
        return render_template('customer_personal_info.html')

# staff registration authentication route 
# note: pattern similar to customer_registerAuth
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
        session['username'] = username
        cursor.execute(ins, (username, password))
        connection.commit()
        cursor.close()
        return render_template('staff_personal_info.html')

# route for customer personal info
@app.route('/customer_personal_info', methods=['GET','POST'])
def customer_personal_info():
    email = session['email']
    info_dict = {}
    info_dict['name'] = request.form['name']
    info_dict['building_number'] = request.form['building_number']
    info_dict['city'] = request.form['city']
    info_dict['state'] = request.form['state']
    info_dict['phone_number'] = request.form['phone_number']
    info_dict['passport_number'] = request.form['passport_number']
    info_dict['passport_country'] = request.form['passport_country']
    info_dict['passport_expiration'] = request.form['passport_expiration']

    cursor = connection.cursor()
    for key in info_dict:
        update = "UPDATE CUSTOMER SET {} = %s WHERE email = %s".format(key)
        cursor.execute(update, (info_dict[key], email))
        connection.commit()
    cursor.close()

    return redirect(url_for('customer_home'))

# global variables for number of phone numbers/emails to be input staff
# route for staff personal info

@app.route('/staff_personal_info', methods = ['POST'])
def staff_personal_info():
    username = session['username']
    info_dict = {}
    info_dict['first_name'] = request.form['first_name']
    info_dict['last_name'] = request.form['last_name']
    info_dict['date_of_birth'] = request.form['date_of_birth']
    info_dict['airline_name'] = request.form['airline_name']
    
    phones = request.form['phones']
    emails = request.form['emails']
    phone_ids=[]
    email_ids=[]

    cursor = connection.cursor()
    for key in info_dict:
        update = "UPDATE staff SET {} = %s WHERE username = %s".format(key)
        cursor.execute(update, (info_dict[key], username))
        connection.commit()
    cursor.close()

    for number in range(int(phones)):
        phone_ids.append(str(number+1))
    
    for number in range(int(emails)):
        email_ids.append('Email '+str(number+1))

    global staff_phones
    global staff_emails

    staff_phones = phone_ids
    staff_emails = email_ids

    return render_template('staff_phones_emails.html', phones=phone_ids, emails=email_ids)

@app.route('/staff_phones_emails', methods = ['POST'])
def staff_phones_emails():
    username = session['username']
    cursor = connection.cursor()

    global staff_phones
    global staff_emails
  
    for id in staff_phones:
        phone_number = request.form[id]
        insert = "INSERT INTO staff_phone_number(username, phone_number) values(%s, %s)"
        cursor.execute(insert, (username, phone_number))
        connection.commit()

    for id in staff_emails:
        email = request.form[id]
        insert = "INSERT INTO staff_email(username, email) values(%s, %s)"
        cursor.execute(insert, (username, email))
        connection.commit()

    cursor.close()
    
    return redirect(url_for('staff_home'))

# ---------------------------------LOGIN-------------------------------------------

# customer login route
@app.route('/customer_login')
def custLogin():
    return render_template('customer_login.html')

# staff login route
@app.route('/staff_login')
def staffLogin():
    return render_template('staff_login.html')

# customer login authentication route
# note: similar to staff_loginAuth
@app.route('/customer_loginAuth', methods=['POST'])
def customer_loginAuth():
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
            return redirect(url_for('customer_home'))
        # case: password does not match --> throw error
        else:
            error = "Incorrect password"
            return render_template('customer_login.html', error = error)
    # case: email does not exist --> throw error
    else:
        error = "Invalid email"
        return render_template('customer_login.html', error = error)

# staff login authentication route
# note: similar to customer_loginAuth
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
            return redirect(url_for('staff_home'))
        else:
            error = "Incorrect password"
            return render_template('staff_login.html', error = error)
    else:
        error = "Invalid username"
        return render_template('staff_login.html', error = error)

# ---------------------------------PUBLIC-------------------------------------------

# public information route
@app.route('/public_info')
def public_info():
    return render_template('public_info.html')

# view flights(public) route
@app.route('/public_view_flights')
def public_view_flights():
    # declaring timestamp for now
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours = 2)
    valid_date = valid_timestamp.date()
    return render_template('public_view_flights.html', today_date = valid_date, available = True)

# route for searching for flights (public)
@app.route('/public_flightsearch', methods = ['GET','POST'])
def public_flightSearch():
    # valid time/date
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours = 2)
    valid_time = valid_timestamp.time()
    valid_date = valid_timestamp.date()

    # dictionary for search parameters
    param_dict = {}
    date_input = {} 
    date_input['departure_date'] = request.form['departure_date']
    param_dict['src_name'] = request.form['src_name']
    param_dict['dst_name'] = request.form['dst_name']

    query = "SELECT * FROM flight "
    search_string = ""
    # list of search parameter keys
    param_keys = []
    # list of search parameter values
    param_values = []
    predicate_start = ""
    predicate_end = ""
    dateinsearch = True

    if len(date_input['departure_date'])<1:
        predicate_start = "WHERE ((departure_date>%s) OR (departure_date=%s AND departure_time>%s))"
        param_values.extend([valid_date, valid_date, valid_time])
        dateinsearch  = False
    else:
        if date_input['departure_date'] == valid_date:
            predicate_start = "WHERE (departure_date = %s AND departure_time>%s)"
            param_values.extend([valid_date, valid_time])
            dateinsearch = False

    if dateinsearch:
        param_dict['departure_date'] = date_input['departure_date']

    for items in param_dict:
        if len(param_dict[items])>1:
            param_keys.append(items)

    if dateinsearch:
        predicate_start = " WHERE {} = %s".format(param_keys[0])
        param_values.append(param_dict[param_keys[0]])

    if len(param_keys)>0:
        for items in param_keys:
            predicate_end += " AND {} = %s".format(items)
            param_values.append(param_dict[items])
        
    param_tuple = tuple(param_values)
    search = query + predicate_start + predicate_end
    cursor = connection.cursor()
    cursor.execute(search, param_tuple)
    data = cursor.fetchall()
    cursor.close()
    available = True

    if len(data)<1:
        available = False

    return render_template('public_view_flights.html', data=data, today_date = valid_date, available = available)

# round trip view flights route
@app.route('/public_view_flightsRT', methods=["GET","POST"])
def public_view_flightsRT():
    return render_template('public_view_flights.html', roundtrip = True, available = True)

# round trip search route
@app.route('/public_flightsearchRT', methods = ['GET','POST'])
def public_flightSearchRT():
    # valid time/date
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours = 2)
    valid_time = valid_timestamp.time()
    valid_date = valid_timestamp.date()
    return_timestamp = timestamp + timedelta(days=1)
    valid_return_date = return_timestamp.date()
    # dictionary for search parameters
    param_dict = {}
    param_dict['src_name'] = request.form['src_name']
    param_dict['dst_name'] = request.form['dst_name']
    date_input = {} 
    date_input['departure_date'] = request.form['departure_date']
    date_input['return_date'] = request.form['return_date']

    # dictionary for return parameters
    return_dict = {}
    return_dict['src_name'] = param_dict['dst_name']
    return_dict['dst_name'] = param_dict['src_name']

    query_out = "SELECT * FROM flight "
    query_re = "SELECT * FROM flight "
    # list of search parameter keys
    param_keys = []
    # list of search parameter values
    param_values = []
    # list of return parameter keys
    return_keys = []
    # list of return parameter values
    return_values = []
    predicate_start = ""
    predicate_end = ""
    predicate_start_re = ""
    predicate_end_re = ""
    dateinsearch = True
    returninsearch = True

    if len(date_input['departure_date'])<1:
        predicate_start = "WHERE ((departure_date>%s) OR (departure_date=%s AND departure_time>%s))"
        param_values.extend([valid_date, valid_date, valid_time])
        dateinsearch  = False
    else:
        if date_input['departure_date'] == valid_date:
            predicate_start = "WHERE (departure_date = %s AND departure_time>%s)"
            param_values.extend([valid_date, valid_time])
            dateinsearch = False

    if dateinsearch:
        param_dict['departure_date'] = date_input['departure_date']

    for items in param_dict:
        if len(param_dict[items])>1:
            param_keys.append(items)

    if dateinsearch:
        predicate_start = " WHERE {} = %s".format(param_keys[0])
        param_values.append(param_dict[param_keys[0]])

    if len(param_keys)>0:
        for items in param_keys:
            predicate_end += " AND {} = %s".format(items)
            param_values.append(param_dict[items])

    for items in return_dict:
        if len(return_dict[items])>1:
            return_keys.append(items)

    if len(date_input['return_date'])<1:
        returninsearch  = False
    else:
        if date_input['return_date'] == valid_return_date:
            returninsearch = False

    if returninsearch:
        predicate_start_re = "WHERE departure_date = %s"
        return_values.append(date_input['return_date'])
        return
    else:
        if dateinsearch:
            valid_return_date = date_input['departure_date'] + timedelta(days=1)
        else:
            pass
        return_values.append(valid_return_date)
        predicate_start_re = "WHERE departure_date >= %s"
    
    if len(return_keys)>0:
        for items in return_keys:
            predicate_end_re += " AND {} = %s".format(items)
            return_values.append(return_dict[items])
            
    search_out = query_out + predicate_start + predicate_end
    search_re = query_re + predicate_start_re + predicate_end_re

    param_tuple = tuple(param_values)
    return_tuple = tuple(return_values)
    cursor = connection.cursor()
    cursor.execute(search_out, param_tuple)
    outgoing = cursor.fetchall()
    cursor.close()
    cursor = connection.cursor()
    cursor.execute(search_re, return_tuple)
    returning = cursor.fetchall()
    cursor.close()

    available = True
    if len(outgoing)<1 or len(returning)<1:
        available = False

    return render_template('public_view_flights.html', data = outgoing, returning = returning, 
        today_date = valid_date, roundtrip = True, valid_return_date = valid_return_date,
        available = available)

@app.route('/public_view_status')
def public_view_status():
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours = 2)
    valid_date = valid_timestamp.date()
    return render_template('public_check_status.html', today_date = valid_date)


@app.route('/public_check_status', methods=['GET', 'POST'])
def public_check_status():
    airline_name = request.form['airline_name']
    flight_number = request.form['flight_number']
    departure_date = request.form['departure_date']
    arrival_date = request.form['arrival_date']

    cursor = connection.cursor()
    query = 'SELECT * FROM flight WHERE airline_name=%s and flight_number=%s and departure_date=%s and arrival_date=%s'
    cursor.execute(query, (airline_name, flight_number, departure_date, arrival_date))
    data = cursor.fetchall()
    cursor.close()
    return render_template('public_check_status.html', data=data)

# ---------------------------------CUSTOMER-------------------------------------------

# customer homepage route
@app.route('/customer_home')
def customer_home():
    email = session['email']
    cursor = connection.cursor()
    query = 'SELECT name FROM customer WHERE email=%s'
    cursor.execute(query, email)
    name = cursor.fetchone()['name']
    return render_template('customer_home.html', name=name)

# ---------------------------------STAFF-------------------------------------------
@app.route('/staff_home', methods=['GET', 'POST'])
def staff_home():
    username = session['username']
    cursor = connection.cursor()
    query1 = 'SELECT first_name, airline_name FROM staff WHERE username=%s'
    cursor.execute(query1, username)
    data = cursor.fetchone()
    first_name = data['first_name']
    airline_name = data['airline_name'] 
    return render_template('staff_home.html', first_name=first_name, airline_name=airline_name)


 # ---------------------------------LOGOUT-------------------------------------------
@app.route('/customer_logout')
def customer_logout():
    session.pop('email')
    return redirect(url_for('index'))

@app.route('/staff_logout')
def staff_logout():
    session.pop('username')
    return redirect(url_for('index'))

 # ----------------------------------------------------------------------------------

if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)