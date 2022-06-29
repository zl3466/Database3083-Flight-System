from crypt import methods
from os import times
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors, hashlib
from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta


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

# ---------------------------------REGISTER-------------------------------------------
# register route
@app.route('/register')
def register():
    return render_template('register.html')

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

    return render_template('index.html')

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
    
    return render_template('index.html')

# ---------------------------------LOGIN-------------------------------------------
# login route
@app.route('/login')
def login():
    return render_template('login.html')

# customer login route
@app.route('/customer_login')
def customer_login():
    return render_template('customer_login.html')

# staff login route
@app.route('/staff_login')
def staff_login():
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
    query = 'SELECT password, airline_name FROM staff where username = %s'
    cursor.execute(query, (username))
    data = cursor.fetchone()
    cursor.close()
    error = None

    if(data):
        if data['password'] == password:
            session['username'] = username
            session['airline_name'] = data['airline_name']
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
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours = 2)
    valid_date = valid_timestamp.date()
    return_timestamp = timestamp + timedelta(days=1)
    valid_return_date = return_timestamp.date()
    return render_template('public_view_flights.html', roundtrip = True, available = True, today_date=valid_date, 
    valid_return_date = valid_return_date)

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
    init_valid_return_date = return_timestamp.date()
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
            valid_rd_object = datetime.strptime(date_input['departure_date'], '%Y-%m-%d')
            valid_return_date =  valid_rd_object + timedelta(days=1)
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
        today_date = valid_date, roundtrip = True, valid_return_date = init_valid_return_date,
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

# ---------------------------------view my flights-------------------------------------------
@app.route('/my_flight', methods=['GET', 'POST'])
def my_flight():
    email = session['email']
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours = 2)
    valid_date = valid_timestamp.date()
    valid_time = valid_timestamp.time()
    now_time = timestamp.time()
    now_date = timestamp.date()
    cursor = connection.cursor()
    query = 'SELECT DISTINCT * FROM ticket as T, flight as F WHERE T.email=%s AND (T.airline_name,T.flight_number,T.departure_date, \
        T.departure_time) = (F.airline_name,F.flight_number,F.departure_date, \
        F.departure_time)'
    # 'T.airline_name=F.airline_name AND T.flight_number=F.flight_number AND T.departure_date=F.departure_date and T.departure_time=F.departure_time'
    # future: depart after 2 hours from now()
    predicate = ' AND (F.departure_date>%s OR (F.departure_date=%s AND F.departure_time>%s))' 
    cursor.execute(query+predicate, (email, valid_date, valid_date, valid_time))
    future = cursor.fetchall()
    
    # current: depart at most 2 hours from now() and land after now()
    predicate = ' AND (F.departure_date<%s OR (F.departure_date=%s AND F.departure_time<=%s))\
        AND (F.arrival_date>%s or (F.arrival_date=%s AND F.arrival_time>%s))' 
    cursor.execute(query+predicate, (email, valid_date, valid_date, valid_time, now_date,
    now_date, now_time))
    current = cursor.fetchall()
    
    # past: landed before now()
    predicate = ' AND (F.arrival_date<%s OR (F.arrival_date=%s AND F.arrival_time<%s))' 
    cursor.execute(query+predicate, (email, now_date, now_date, now_time))
    past = cursor.fetchall()
    cursor.close()
    return render_template('customer_my_flights.html', future=future, current=current, past=past)

@app.route('/cancel_flight', methods=['GET', 'POST'])
def cancel_flight():
    ticket_id = request.form['ticket_id']
    cursor = connection.cursor()
    # query = 'delete from ticket where ticket_id=%s'
    query = 'update ticket set card_type=%s, card_number=%s, exp_date=%s, purchase_date=%s, purchase_time=%s, email=%s ' \
            'where ticket_id=%s'
    cursor.execute(query, (None, None, None, None, None, None, ticket_id))
    
    # decreasing ticket_count
    query = 'SELECT * FROM flight NATURAL JOIN ticket WHERE ticket_id=%s'
    cursor.execute(query,ticket_id)
    data = cursor.fetchone()
    count = data['ticket_count']
    count -= 1
    airline_name = data['airline_name']
    flight_number = data['flight_number']
    departure_date = data['departure_date']
    departure_time = data['departure_time']
    update_ticket_count = 'UPDATE flight SET ticket_count=%s WHERE (airline_name,\
        flight_number, departure_date,departure_time)=(%s,%s,%s,%s)'
    cursor.execute(update_ticket_count,(count,airline_name,flight_number,departure_date,departure_time))
    connection.commit()
    cursor.close()
    return redirect(url_for('my_flight'))

# ---------------------------------search flights-------------------------------------------
@app.route('/customer_oneway')
def customer_oneway():
    return render_template('customer_search_flight.html', available=True)


@app.route('/customer_rt')
def customer_rt():
    return render_template('customer_search_flight.html', roundtrip=True, available=True)

@app.route('/customer_search_flight', methods=['GET', 'POST'])
def customer_search_flight():
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

    return render_template('customer_search_flight.html', data=data, available = available, today_date=valid_date)

@app.route('/customer_search_flight_rt', methods=['GET', 'POST'])
def customer_search_flight_rt():
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
            valid_rd_object = datetime.strptime(date_input['departure_date'], '%Y-%m-%d')
            valid_return_date =  valid_rd_object + timedelta(days=1)        
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

    return render_template('customer_search_flight.html', data = outgoing, returning = returning, 
        today_date = valid_date, roundtrip = True, valid_return_date = valid_return_date,
        available = available)

# ---------------------------------purchase ticket-------------------------------------------
# helper function to determine ticket pricing
def ticket_pricing(airline_name,  flight_number, departure_date, departure_time, base_price):
    query = "SELECT seats, ticket_count FROM airplane AS A, flight AS F \
        WHERE A.airline_name = F.airline_name AND A.plane_id=F.plane_id AND F.airline_name=%s \
        AND departure_date=%s AND departure_time=%s AND flight_number=%s"
    cursor = connection.cursor()
    cursor.execute(query,(airline_name,departure_date,departure_time,flight_number))
    data = cursor.fetchone()
    cursor.close()

    seats = int(data['seats'])
    ticket_count = int(data['ticket_count'])
    current_capacity = (seats - ticket_count)/seats
    multiplier = 1
    sold_price = 0
    if current_capacity <= 0.4:
        multiplier = 1.2

    sold_price = base_price * multiplier
    current_capacity = 1 - current_capacity

    return [seats, current_capacity*100, multiplier, base_price, sold_price]

# unfinished purchase()
@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    data = {}
    airline_name = data['airline_name'] = request.form['airline_name']
    flight_number = data['flight_number'] = request.form['flight_number']
    departure_date = data['departure_date'] = request.form['departure_date']
    departure_time = data['departure_time'] = request.form['departure_time']
    base_price = data['base_price'] = int(request.form['base_price'])

    bill = ticket_pricing(airline_name, flight_number, departure_date, departure_time, base_price)

    return render_template('customer_purchase.html', data=data, bill = bill)

@app.route('/make_purchase', methods=['GET', 'POST'])
def make_purchase():
    email = session['email']
    timestamp = datetime.now()
    now_time = timestamp.time()
    now_date = timestamp.date()
    # get payment info
    card_type = request.form['card_type']
    card_number = request.form['card_number']
    card_name = request.form['card_name']
    exp_date = request.form['exp_date']

    # get flight info
    airline_name = request.form['airline_name']
    flight_number = request.form['flight_number']
    departure_date = request.form['departure_date']
    departure_time = request.form['departure_time']
    sold_price = int(request.form['sold_price'])

    cursor = connection.cursor()
    # get new ticket id
    query = 'SELECT ticket_id FROM ticket WHERE airline_name=%s AND flight_number=%s \
        AND departure_date=%s AND departure_time=%s AND email IS NULL'
    cursor.execute(query, (airline_name, flight_number, departure_date, departure_time))
    ticket = cursor.fetchone()['ticket_id']
    error = None
    if ticket is not None:
        # inputting information for available ticket
        update_ticket = 'UPDATE ticket SET email=%s, card_type=%s, card_number=%s, \
            card_name=%s, exp_date=%s, purchase_time=%s, purchase_date=%s, sold_price=%s \
            WHERE ticket_id=%s'
        cursor.execute(update_ticket,(email,card_type,card_number,card_name,exp_date,now_time,
        now_date,sold_price,ticket))
        connection.commit()
        # increasing ticket_count
        query = 'SELECT ticket_count FROM flight WHERE (airline_name,flight_number, \
            departure_date,departure_time)=(%s,%s,%s,%s)'
        cursor.execute(query,(airline_name,flight_number,departure_date,departure_time))
        count = int(cursor.fetchone()['ticket_count'])
        count += 1
        update_ticket_count = 'UPDATE flight SET ticket_count=%s WHERE (airline_name,\
            flight_number, departure_date,departure_time)=(%s,%s,%s,%s)'
        cursor.execute(update_ticket_count,(count,airline_name,flight_number,departure_date,departure_time))
        connection.commit()
    else:
        error = 'No more tickets for this flight'
    cursor.close()
    # return render_template('customer_search_flight.html')
    return render_template('customer_search_flight.html', error = error)


# ---------------------------------rate / comment-------------------------------------------
@app.route('/rate_comment', methods=['GET', 'POST'])
def rate_comment():
    ticket_id = request.form['ticket_id']
    return render_template('customer_rate_comment.html', ticket_id=ticket_id)


@app.route('/make_rate_comment', methods=['GET', 'POST'])
def make_rate_comment():
    ticket_id = request.form['ticket_id']
    rating = request.form['rating']
    comment = request.form['comment']

    cursor = connection.cursor()
    if comment is None:
        query = 'update ticket set rating=%s where ticket_id=%s'
        cursor.execute(query, (rating, ticket_id))
    else:
        query = 'update ticket set rating=%s and comment=%s where ticket_id=%s'
        cursor.execute(query, (rating, comment, ticket_id))
    message = 'Thanks for your comment!'
    cursor.close()
    return render_template('/make_rate_comment', message=message)


# ---------------------------------track spending-------------------------------------------
@app.route('/customer_track_spending', methods=['GET', 'POST'])
def customer_track_spending():
    return render_template('customer_track_spending.html')


@app.route('/spending_define_period', methods=['GET', 'POST'])
def spending_define_period():
    period = request.form['period']
    return render_template('customer_track_spending.html', period=period)


@app.route('/check_spending_month', methods=['GET', 'POST'])
def check_spending_month():
    email = session['email']
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours=2)
    valid_time = valid_timestamp.time()
    valid_date = valid_timestamp.date()
    start_date = valid_date - relativedelta(months=1)
    cursor = connection.cursor()

    query = 'SELECT SUM(sold_price) FROM ticket WHERE email=%s and ' \
            '((purchase_date>%s) OR (purchase_date=%s and purchase_time>%s))'
    cursor.execute(query, (email, start_date, start_date, valid_time))
    data = cursor.fetchone()
    cursor.close()
    if data['SUM(sold_price)']:
        return render_template('customer_track_spending.html', data=data['SUM(sold_price)'])
    else:
        return render_template('customer_track_spending.html', error='No Purchase Record')


@app.route('/check_spending_year', methods=['GET', 'POST'])
def check_spending_year():
    email = session['email']
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours=2)
    valid_time = valid_timestamp.time()
    valid_date = valid_timestamp.date()
    start_date = valid_date - relativedelta(years=1)
    cursor = connection.cursor()

    query = 'SELECT SUM(sold_price) FROM ticket WHERE email=%s and ' \
            '((purchase_date>%s) OR (purchase_date=%s and purchase_time>%s))'
    cursor.execute(query, (email, start_date, start_date, valid_time))
    data = cursor.fetchone()
    cursor.close()

    if data['SUM(sold_price)']:
        return render_template('customer_track_spending.html', data=data['SUM(sold_price)'])
    else:
        return render_template('customer_track_spending.html', error='No Purchase Record')


@app.route('/check_spending_specific', methods=['GET', 'POST'])
def check_spending_specific():
    email = session['email']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    cursor = connection.cursor()

    query = 'SELECT SUM(sold_price) FROM ticket WHERE email=%s and purchase_date<%s and' \
            '(purchase_date>%s OR purchase_date=%s)'
    cursor.execute(query, (email, end_date, start_date, start_date))
    data = cursor.fetchone()
    cursor.close()

    if data['SUM(sold_price)']:
        return render_template('customer_track_spending.html', data=data['SUM(sold_price)'])
    else:
        return render_template('customer_track_spending.html', error='No Purchase Record')

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

@app.route('/staff_view_flight', methods=['GET', 'POST'])
def staff_view_flight():
    # declaring timestamp for now
    airline_name = session['airline_name']
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours=2)
    valid_time = valid_timestamp.time()
    valid_date = valid_timestamp.date()
    end_date = timestamp + timedelta(days=30)

    cursor = connection.cursor()
    # query to get all upcoming flight data
    # upcoming classified as flights that depart more than 2 hours from now()
    query = 'SELECT * FROM flight WHERE ((departure_date>%s) OR (departure_date=%s AND departure_time>%s))  \
            AND airline_name=%s AND departure_date<%s'
    cursor.execute(query, (valid_date, valid_date, valid_time, airline_name, end_date))
    future = cursor.fetchall()

    default = "(Default range: Next 30 days)"

    return render_template('staff_view_flight.html', future=future, today_date=valid_date, available=True, 
                            default_range = default, airline_name=airline_name)

# route for searching future flights
# future flights -- flights that depart within given range (minimum 2 hours from now())
@app.route('/staff_search_flight', methods=['GET', 'POST'])
def staff_search_flight():
   # valid time/date
    airline_name = session['airline_name']
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours = 2)
    valid_time = valid_timestamp.time()
    valid_date = valid_timestamp.date()

    # dictionary for search parameters
    param_dict = {}
    date_input = {} 
    date_input['start_date'] = request.form['start_date']
    date_input['end_date'] = request.form['end_date']
    param_dict['src_name'] = request.form['src_name']
    param_dict['dst_name'] = request.form['dst_name']

    query = "SELECT * FROM flight "
    # list of search parameter keys
    param_keys = []
    # list of search parameter values
    param_values = []
    predicate_start = ""
    predicate_end = ""

    startinsearch = True
    endinsearch = True

    if len(date_input['start_date'])<1:
        predicate_start = "WHERE ((departure_date>%s) OR (departure_date=%s AND departure_time>%s))"
        param_values.extend([valid_date, valid_date, valid_time])
        startinsearch  = False
    else:
        if date_input['start_date'] == valid_date:
            predicate_start = "WHERE (departure_date = %s AND departure_time>%s)"
            param_values.extend([valid_date, valid_time])
            startinsearch = False
    
    if startinsearch:
        predicate_start = "WHERE (departure_date>=%s)"
        param_values.append(date_input['start_date'])
    
    if len(date_input['end_date'])<1:
        endinsearch = False
    else:
        if date_input['end_date'] == valid_date:
            predicate_end += " AND (departure_date = %s AND departure_time>%s)"
            param_values.extend([valid_date, valid_time])
            endinsearch = False

    if endinsearch:
        predicate_end += " AND (departure_date<=%s)"
        param_values.append(date_input['end_date'])

    predicate_end += " AND airline_name=%s"
    param_values.append(airline_name)

    for items in param_dict:
        if len(param_dict[items])>1:
            param_keys.append(items)

    src = ""
    dst = ""

    if len(param_keys)>0:
        for items in param_keys:
            predicate_end += " AND {} = %s".format(items)
            param_values.append(param_dict[items])
            if items == 'src_name':
                src = param_dict[items]
            if items == 'dst_name':
                dst = param_dict[items]
        
    param_tuple = tuple(param_values)
    search = query + predicate_start + predicate_end
    cursor = connection.cursor()
    cursor.execute(search, param_tuple)
    future = cursor.fetchall()
    cursor.close()
    available = True

    if len(future)<1:
        available = False
    
    return render_template('staff_view_flight.html',today_date=valid_date, future=future, available=available, 
                            initial_src=src, initial_dst=dst,airline_name=airline_name)

@app.route('/staff_current_flight')
def staff_current_flight():
    airline_name = session['airline_name']
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours=2)
    valid_time = valid_timestamp.time()
    valid_date = valid_timestamp.date()
    now_time = timestamp.time()

    cursor = connection.cursor()
    # query to get current flights
    # current flights classified as flights depart at most 2 hours before now() \
    # and that land after now() 
    query = 'SELECT * FROM flight WHERE ((departure_date<%s) OR (departure_date=%s AND departure_time<=%s))  \
            AND airline_name=%s AND ((arrival_date>%s) OR (arrival_date=%s AND arrival_time>%s))' 
    cursor.execute(query, (valid_date, valid_date, valid_time, airline_name, valid_date, valid_date, now_time))
    current = cursor.fetchall()
    return render_template('staff_current_flight.html', current = current, available =True, airline_name=airline_name)

@app.route('/staff_search_current', methods=['GET','POST'])
def staff_search_current():
    airline_name = session['airline_name']
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours=2)
    valid_time = valid_timestamp.time()
    valid_date = valid_timestamp.date()
    now_time = timestamp.time()
    now_date = timestamp.date()
    
    param_dict = {}
    param_keys =[]
    param_dict['src_name'] = request.form['src_name']
    param_dict['dst_name'] = request.form['dst_name']

    query = 'SELECT * FROM flight WHERE ((departure_date<%s) OR (departure_date=%s AND departure_time<=%s))  \
            AND airline_name=%s AND ((arrival_date>%s) OR (arrival_date=%s AND arrival_time>%s))' 
    param_values = [valid_date, valid_date, valid_time, airline_name, now_date, now_date, now_time]
    predicate_end = ""

    for items in param_dict:
        if len(param_dict[items])>1:
            param_keys.append(items)

    src = ""
    dst = ""

    if len(param_keys)>0:
        for items in param_keys:
            predicate_end += " AND {} = %s".format(items)
            param_values.append(param_dict[items])
            if items == 'src_name':
                src = param_dict[items]
            if items == 'dst_name':
                dst = param_dict[items]

    param_tuple = tuple(param_values)
    query += predicate_end
    cursor = connection.cursor()
    cursor.execute(query,param_tuple)
    current = cursor.fetchall()
    cursor.close()

    available = True
    if len(current)<1:
        available = False

    return render_template('staff_current_flight.html', current = current, initial_src=src,initial_dst=dst, 
                            available=available, airline_name=airline_name)

# route for past flights
# default shows all
@app.route('/staff_past_flight')
def staff_past_flight():
    airline_name = session['airline_name']
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours=2)
    now_time = timestamp.time()
    now_date = timestamp.date()

    cursor = connection.cursor()
    # query to get past flight data
    # past flights classified as flights that landed before now()
    query = 'SELECT * FROM flight WHERE ((arrival_date<%s) OR (arrival_date=%s AND arrival_time<=%s))  \
            AND airline_name=%s'
    cursor.execute(query, (now_date, now_date, now_time, airline_name))
    past = cursor.fetchall()

    cursor.close()
    return render_template('staff_past_flight.html', past = past, today_date=now_date,airline_name=airline_name)

# route for searching past flights
# for given range(start_date,end_date), query will display flights that depart
# from start_date and have landed by end_date
@app.route('/staff_search_past', methods=['GET', 'POST'])
def staff_search_past():
   # valid time/date
    airline_name = session['airline_name']
    timestamp = datetime.now()
    now_time = timestamp.time()
    now_date = timestamp.date()

    # dictionary for search parameters
    param_dict = {}
    date_input = {} 
    date_input['start_date'] = request.form['start_date']
    date_input['end_date'] = request.form['end_date']
    param_dict['src_name'] = request.form['src_name']
    param_dict['dst_name'] = request.form['dst_name']

    query = "SELECT * FROM flight WHERE airline_name=%s"
    # list of search parameter keys
    param_keys = []
    # list of search parameter values
    param_values = [airline_name]
    predicate = ""

    startinsearch = True
    endinsearch = True

    if len(date_input['start_date'])<1:
        startinsearch  = False
    else:
        if date_input['start_date'] == now_date:
            predicate += " AND departure_date=%s"
            param_values.append(now_date)
            startinsearch = False
    
    if startinsearch:
        predicate += " AND departure_date>=%s"
        param_values.append(date_input['start_date'])

    if len(date_input['end_date'])<1:
        predicate += " AND (arrival_date<%s OR (arrival_date=%s AND arrival_time<%s))"
        param_values.extend([now_date(), now_date(), now_time])
        endinsearch = False
    else:
        if date_input['end_date'] == now_date:
            predicate += " AND (arrival_date=%s AND arrival_time<%s)"
            param_values.extend([now_date, now_time])
            endinsearch = False

    if endinsearch:
        predicate += " AND arrival_date<=%s"
        param_values.append(date_input['end_date'])

    for items in param_dict:
        if len(param_dict[items])>1:
            param_keys.append(items)

    src = ""
    dst = ""

    if len(param_keys)>0:
        for items in param_keys:
            predicate += " AND {} = %s".format(items)
            param_values.append(param_dict[items])
            if items == 'src_name':
                src = param_dict[items]
            if items == 'dst_name':
                dst = param_dict[items]
        
    param_tuple = tuple(param_values)
    search = query + predicate
    cursor = connection.cursor()
    cursor.execute(search, param_tuple)
    past = cursor.fetchall()
    cursor.close()
    available = True

    if len(past)<1:
        available = False

    return render_template('staff_past_flight.html',today_date=now_date, past=past, available=available, 
                            initial_src=src, initial_dst=dst, airline_name=airline_name)

# ---------------------------------change status-------------------------------------------

@app.route('/change_status', methods=['GET', 'POST'])
def change_status():
    new_status = request.form['status']
    airline_name = session['airline_name']
    flight_number = request.form['flight_number']
    departure_date = request.form['departure_date']
    departure_time = request.form['departure_time']
    if new_status is not None:
        cursor = connection.cursor()
        query = 'update flight set status=%s where airline_name=%s and flight_number=%s ' \
                'and departure_date=%s and departure_time=%s'
        cursor.execute(query, (new_status, airline_name, flight_number, departure_date, departure_time))
        connection.commit()
        cursor.close()
    return redirect(url_for('staff_view_flight'))

# ---------------------------------view customers-------------------------------------------

@app.route('/flight_view_customers', methods=['GET','POST'])
def flight_view_customer():
    airline_name = session['airline_name']
    flight_number = request.form['flight_number']
    departure_date = request.form['departure_date']
    departure_time = request.form['departure_time']
    query = 'SELECT C.name, C.email FROM customer as C, ticket as T, flight as F WHERE C.email = T.email \
            AND T.airline_name = F.airline_name AND T.flight_number = F.flight_number AND \
            T.departure_date = F.departure_date AND T.departure_time = F.departure_time AND \
            F.airline_name = %s AND F.flight_number = %s AND F.departure_date = %s AND \
            F.departure_time = %s'

    cursor = connection.cursor()
    cursor.execute(query,(airline_name, flight_number, departure_date, departure_time))
    data = cursor.fetchall()
    cursor.close()
    return render_template('staff_flight_customer_list.html', data = data, flight_number = flight_number,
                            departure_date = departure_date, departure_time = departure_time)

# ---------------------------------add plane-------------------------------------------

@app.route('/go_add_plane')
def go_add_plane():
    return render_template('staff_add_plane.html')


@app.route('/add_plane', methods=['GET', 'POST'])
def add_plane():
    airline_name = session['airline_name']
    plane_id = request.form['plane_id']
    seat_num = request.form['seat_num']
    manufacturer = request.form['manufacturer']
    age = request.form['age']
    cursor = connection.cursor()
    query1 = 'select * from airplane where plane_id=%s'
    cursor.execute(query1, plane_id)
    plane = cursor.fetchone()
    if plane is not None:
        message = 'Error: Plane Already Exist!'
    else:
        query2 = 'insert into airplane values(%s, %s, %s, %s, %s)'
        cursor.execute(query2, (airline_name, plane_id, seat_num, manufacturer, age))
        connection.commit()
        message = 'Plane Added Successfully'
    cursor.close()
    return render_template('staff_add_plane.html', message=message)

# ---------------------------------add flight-------------------------------------------
@app.route('/go_add_flight')
def go_add_flight():
    return render_template('staff_add_flight.html')

# helper function to generate ticket_ids for flights
def generateTickets(airline_name, flight_number, departure_date, departure_time, seats):
    cursor = connection.cursor()
    for number in range(seats):
        ticket_id = airline_name + flight_number + departure_date + departure_time + str(number)
        ins = "INSERT INTO ticket(ticket_id, airline_name, flight_number, departure_date, departure_time) \
                VALUES(%s,%s,%s,%s,%s)"
        cursor.execute(ins,(ticket_id,airline_name, flight_number, departure_date, departure_time))
        connection.commit()
    cursor.close()
    return

@app.route('/add_flight', methods=['GET', 'POST'])
def add_flight():
    airline_name = session['airline_name']
    flight_number = request.form['flight_number']
    departure_date = request.form['departure_date']
    departure_time = request.form['departure_time']
    arrival_date = request.form['arrival_date']
    arrival_time = request.form['arrival_time']
    base_price = request.form['base_price']
    plane_id = request.form['plane_id']
    status = request.form['status']
    src_airport = request.form['src_airport']
    dst_airport = request.form['dst_airport']

    cursor = connection.cursor()

    # check plane exist, and duplicate flight
    query1 = 'select * from flight where airline_name=%s and flight_number=%s ' \
                'and departure_date=%s and departure_time=%s'
    cursor.execute(query1, (airline_name, flight_number, departure_date, departure_time))
    the_flight = cursor.fetchone()
    if the_flight is not None:
        message = 'Error: This Flight Already Exists!'
    else:
        ticket_count = 0
        query2 = 'insert into flight values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(query2, (airline_name, flight_number, departure_date, departure_time, base_price,
                                plane_id, status, ticket_count, arrival_date, arrival_time,
                                dst_airport, src_airport))
        connection.commit()
        query3 = 'SELECT seats FROM airplane WHERE plane_id=%s AND airline_name=%s'
        cursor.execute(query3, (plane_id, airline_name))
        seats = cursor.fetchone()
        generateTickets(airline_name, flight_number, departure_date, departure_time, int(seats['seats']))
        message = 'Flight Added Successfully'
    cursor.close()
    return render_template('staff_add_flight.html', message=message)

# ---------------------------------add airport-------------------------------------------
@app.route('/go_add_airport')
def go_add_airport():
    return render_template('staff_add_airport.html')


@app.route('/add_airport', methods=['GET', 'POST'])
def add_airport():
    name = request.form['name']
    city = request.form['city']
    country = request.form['country']
    type = request.form['type']

    cursor = connection.cursor()

    query1 = 'select * from airport where name=%s'
    cursor.execute(query1, name)
    duplicate = cursor.fetchone()
    if duplicate is not None:
        message = 'This Airport Already Exist in System'
    else:
        query2 = 'insert into airport values(%s, %s, %s, %s)'
        cursor.execute(query2, (name, city, country, type))
        connection.commit()
        message = 'Airport Added Successfully'
    cursor.close()
    return render_template('staff_add_airport.html', message=message)

# ---------------------------------view ratings-------------------------------------------
@app.route('/go_view_ratings')
def go_view_ratings():
    return render_template('staff_view_ratings.html')

@app.route('/view_ratings', methods=['GET', 'POST'])
def view_ratings():
    airline_name = session['airline_name']
    flight_number = request.form['flight_number']
    departure_date = request.form['departure_date']
    departure_time = request.form['departure_time']

    cursor = connection.cursor()

    query1 = 'select * from ticket where airline_name=%s and flight_number=%s ' \
             'and departure_date=%s and departure_time=%s and rating!=%s'
    cursor.execute(query1, (airline_name, flight_number, departure_date, departure_time, 'null'))
    data = cursor.fetchall()
    if len(data) == 0:
        cursor.close()
        error = 'No such flight or ratings yet'
        return render_template('staff_view_ratings.html', error=error)
    else:
        ticket = data[0]
        avg = round(sum(line['rating'] for line in data) / len(data), 2)
        cursor.close()
        return render_template('staff_view_ratings.html', data=data, avg=avg, ticket=ticket)

# ---------------------------------view frequent customer-------------------------------------------
@app.route('/go_frequent_customers', methods=['GET', 'POST'])
def go_frequent_customers():
    airline_name = session['airline_name']
    cursor = connection.cursor()
    query = 'select email, count(ticket_id), sum(sold_price) from ticket where email !=%s and airline_name=%s ' \
            'group by email order by count(ticket_id) DESC'
    cursor.execute(query, ('null', airline_name))
    customers = cursor.fetchall()
    return render_template('staff_view_frequent_customers.html', customers=customers)


@app.route('/view_customer_records', methods=['GET', 'POST'])
def view_customer_records():
    airline_name = session['airline_name']
    email = request.form['email']
    cursor = connection.cursor()
    query = 'select * from ticket where email =%s and airline_name=%s '
    cursor.execute(query, (email, airline_name))
    record = cursor.fetchall()
    return render_template('staff_view_customer_records.html', record=record, email=email)

# ---------------------------------view report-------------------------------------------
@app.route('/go_view_reports')
def go_view_reports():
    return render_template('staff_view_reports.html')


@app.route('/sale_define_period', methods=['GET', 'POST'])
def sale_define_period():
    period = request.form['period']
    return render_template('staff_view_reports.html', period=period)


@app.route('/view_report_month', methods=['GET', 'POST'])
def view_record_month():
    airline_name = session['airline_name']
    timestamp = datetime.now()
    valid_timestamp = timestamp
    valid_time = valid_timestamp.time()
    valid_date = valid_timestamp.date()
    start_date = valid_date - relativedelta(months=1)
    cursor = connection.cursor()

    query = 'SELECT count(ticket_id) FROM ticket WHERE airline_name=%s and email!=%s and ' \
            '((purchase_date>%s) OR (purchase_date=%s and purchase_time>%s))'
    cursor.execute(query, (airline_name, 'null', start_date, start_date, valid_time))
    data = cursor.fetchone()
    cursor.close()
    if data['count(ticket_id)']:
        return render_template('staff_view_reports.html', data=data['count(ticket_id)'])
    else:
        return render_template('staff_view_reports.html', error='No Sales Record in Selected Period')


@app.route('/view_report_year', methods=['GET', 'POST'])
def view_record_year():
    airline_name = session['airline_name']
    timestamp = datetime.now()
    valid_timestamp = timestamp
    valid_time = valid_timestamp.time()
    valid_date = valid_timestamp.date()
    start_date = valid_date - relativedelta(years=1)
    cursor = connection.cursor()

    query = 'SELECT count(ticket_id) FROM ticket WHERE airline_name=%s and email!=%s and ' \
            '((purchase_date>%s) OR (purchase_date=%s and purchase_time>%s))'
    cursor.execute(query, (airline_name, 'null', start_date, start_date, valid_time))
    data = cursor.fetchone()
    cursor.close()

    if data['count(ticket_id)']:
        return render_template('staff_view_reports.html', data=data['count(ticket_id)'])
    else:
        return render_template('staff_view_reports.html', error='No Sales Record in Selected Period')


@app.route('/view_report_specific', methods=['GET', 'POST'])
def view_record_specific():
    airline_name = session['airline_name']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    cursor = connection.cursor()

    query = 'SELECT count(ticket_id) FROM ticket WHERE airline_name=%s and email!=%s and ' \
            '((purchase_date>%s) OR (purchase_date=%s and purchase_time>%s))'
    cursor.execute(query, (airline_name, 'null', end_date, start_date, start_date))
    data = cursor.fetchone()
    cursor.close()

    if data['count(ticket_id)']:
        return render_template('staff_view_reports.html', data=data['count(ticket_id)'])
    else:
        return render_template('staff_view_reports.html', error='No Sales Record in Selected Period')

# ---------------------------------view revenue-------------------------------------------
@app.route('/go_view_revenue', methods=['GET', 'POST'])
def go_view_revenue():
    airline_name = session['airline_name']
    timestamp = datetime.now()
    valid_timestamp = timestamp
    valid_time = valid_timestamp.time()
    valid_date = valid_timestamp.date()
    last_month = valid_date - relativedelta(months=1)
    last_year = valid_date - relativedelta(years=1)
    cursor = connection.cursor()

    query = 'select sum(sold_price) from ticket where airline_name=%s and email!=%s and ' \
            '((purchase_date>%s) OR (purchase_date=%s and purchase_time>%s))'

    cursor.execute(query, (airline_name, 'null', last_month, last_month, valid_time))
    monthly_revenue = cursor.fetchone()

    cursor.execute(query, (airline_name, 'null', last_year, last_year, valid_time))
    annual_revenue = cursor.fetchone()

    revenue_list = []
    query2 = 'select sum(sold_price) from ticket where airline_name=%s and email!=%s and ' \
             '((purchase_date>%s) OR (purchase_date=%s and purchase_time>%s)) and ' \
             '((purchase_date<%s) OR (purchase_date=%s and purchase_time<%s))'

    time_zero = valid_time.replace(hour=0, minute=0, second=0, microsecond=0)
    for i in range(1, 13):
        the_month_start = (valid_date - relativedelta(months=i)).replace(day=1)
        the_month_end = (the_month_start + relativedelta(months=1)).replace(day=1)

        cursor.execute(query2, (airline_name, 'null', the_month_start, the_month_start, time_zero,
                                the_month_end, the_month_end, time_zero))
        the_revenue = cursor.fetchone()
        date_range = str(the_month_start) + ' to ' + str(the_month_end)
        if the_revenue['sum(sold_price)'] is None:
            the_revenue = 0
        else:
            the_revenue = the_revenue['sum(sold_price)']
        revenue_list.insert(0, (date_range, the_revenue))

    if len(monthly_revenue) != 0 and len(annual_revenue) != 0:
        return render_template('staff_view_revenue.html', monthly_revenue=monthly_revenue['sum(sold_price)'],
                               annual_revenue=annual_revenue['sum(sold_price)'], revenue_list=revenue_list)
    else:
        return render_template('staff_view_revenue.html', error='Failed to Collect Data')

 # ---------------------------------LOGOUT-------------------------------------------
@app.route('/customer_logout')
def customer_logout():
    session.pop('email')
    return redirect(url_for('customer_login'))

@app.route('/staff_logout')
def staff_logout():
    session.pop('username')
    return redirect(url_for('staff_login'))

 # ----------------------------------------------------------------------------------

if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)