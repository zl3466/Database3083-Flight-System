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

@app.route('/customer_view_flights')
def customer_view_flights():
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours = 2)
    valid_date = valid_timestamp.date()
    return render_template('customer_view_flights.html', today_date = valid_date, available = True)

@app.route('/customer_oneway')
def customer_oneway():
    return render_template('customer_search_flight.html')


@app.route('/customer_rt')
def customer_rt():
    return render_template('customer_search_flight.html', round_trip=True)


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

    return render_template('customer_search_flight.html', data=data, available = available)


@app.route('/customer_search_flight_rt', methods=['GET', 'POST'])
def customer_search_flight_rt():
    # dictionary for search parameters
    param_dict = {}
    param_dict['src_name'] = request.form['src_name']
    param_dict['dst_name'] = request.form['dst_name']
    param_dict['departure_date'] = request.form['departure_date']
    # dictionary for return search parameters
    param_dictRT = {}
    param_dictRT['dst_name'] = request.form['src_name']
    param_dictRT['src_name'] = request.form['dst_name']
    param_dictRT['departure_date'] = request.form['return_date']

    query = "SELECT * FROM flight AS T, flight AS S WHERE T.src_name = S.dst_name\
                  and T.dst_name = S.src_name"
    # query2 = "SELECT * FROM flight"
    search_string = ""
    # list of search parameter keys
    param_keys = []
    # list of search parameter values
    param_values = []
    for items in param_dict:
        if len(param_dict[items]) > 1:
            param_keys.append(items)
    if len(param_keys) > 0:
        search_string = " WHERE {} = %s".format(param_keys[0])
        param_values.append(param_dict[param_keys[0]])
    if len(param_keys) > 1:
        for items in param_keys[1:]:
            search_string += " and {} = %s".format(items)
            param_values.append(param_dict[items])
    param_tuple = tuple(param_values)
    search = query + search_string
    cursor = connection.cursor()
    cursor.execute(search, param_tuple)
    data = cursor.fetchall()
    cursor.close()
    return render_template('customer_search_flight.html', data=data, roundtrip=True)


@app.route('/go_my_flight', methods=['GET', 'POST'])
def go_my_flight():
    return render_template('customer_my_flights.html')

@app.route('/my_flight', methods=['GET', 'POST'])
def my_flight():
    email = session['email']
    cursor = connection.cursor()
    query = 'select * from ticket where email=%s'
    cursor.execute(query, email)
    data = cursor.fetchall()
    cursor.close()
    return render_template('customer_my_flights.html', data=data)


@app.route('/past_flight', methods=['GET', 'POST'])
def past_flight():
    email = session['email']
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours=2)
    valid_time = valid_timestamp.time()
    valid_date = valid_timestamp.date()

    cursor = connection.cursor()
    query = 'select * from ticket where email=%s and ((departure_date<%s) OR (departure_date=%s and departure_time<%s))'
    cursor.execute(query, (email, valid_date, valid_date, valid_time))
    if cursor.fetchone() is None:
        error = 'No Past Flight Record'
        return render_template('customer_past_flights.html', error=error)
    else:
        data = cursor.fetchall()
        cursor.close()
        return render_template('customer_past_flights.html', data=data)


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

@app.route('/cancel_flight', methods=['GET', 'POST'])
def cancel_flight():
    ticket_id = request.form['ticket_id']
    cursor = connection.cursor()
    # query = 'delete from ticket where ticket_id=%s'
    query = 'update ticket set card_type=%s, card_number=%s, exp_date=%s, purchase_date=%s, purchase_time=%s, email=%s ' \
            'where ticket_id=%s'
    cursor.execute(query, (None, None, None, None, None, None, ticket_id))
    connection.commit()
    cursor.close()
    return render_template('customer_my_flights.html')


@app.route('/customer_track_spending', methods=['GET', 'POST'])
def customer_track_spending():
    return render_template('customer_track_spending.html')


@app.route('/define_period', methods=['GET', 'POST'])
def define_period():
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

# unfinished purchase()
@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    data = {}
    data['airline_name'] = request.form['airline_name']
    data['flight_number'] = request.form['flight_number']
    data['departure_date'] = request.form['departure_date']
    data['departure_time'] = request.form['departure_time']
    data['base_price'] = request.form['base_price']

    return render_template('customer_purchase.html', data=data)


@app.route('/make_purchase', methods=['GET', 'POST'])
def make_purchase():
    email = session['email']

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
    base_price = request.form['base_price']

    cursor = connection.cursor()

    # get new ticket id
    query1 = 'select max(ticket_id) from ticket'
    cursor.execute(query1)
    last_ticket = cursor.fetchone()

    if len(last_ticket) > 0:
        last_ticket_id = last_ticket['max(ticket_id)']
    else:
        last_ticket_id = 0
    new_ticket_id = last_ticket_id + 1

    # get present timestamp
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours=2)
    valid_time = valid_timestamp.time()
    valid_date = valid_timestamp.date()

    query2 = 'insert into ticket (ticket_id, card_type, card_number, card_name, exp_date, purchase_date, ' \
             'purchase_time, email, airline_name, flight_number, departure_date, departure_time, sold_price)' \
             'values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    cursor.execute(query2, (new_ticket_id, card_type, card_number, card_name, exp_date, valid_date,
                            valid_time, email, airline_name, flight_number, departure_date, departure_time, base_price))
    connection.commit()
    cursor.close()
    return render_template('customer_search_flight.html')




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

    return render_template('staff_view_flight.html', future=future, today_date=valid_date, available=True)

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
                            initial_src=src, initial_dst=dst)

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
    return render_template('staff_current_flight.html', current = current, available =True)

@app.route('/staff_search_current', methods=['GET','POST'])
def staff_search_current():
    airline_name = session['airline_name']
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours=2)
    valid_time = valid_timestamp.time()
    valid_date = valid_timestamp.date()
    now_time = timestamp.time()
    
    param_dict = {}
    param_keys =[]
    param_dict['src_name'] = request.form['src_name']
    param_dict['dst_name'] = request.form['dst_name']

    query = 'SELECT * FROM flight WHERE ((departure_date<%s) OR (departure_date=%s AND departure_time<=%s))  \
            AND airline_name=%s AND ((arrival_date>%s) OR (arrival_date=%s AND arrival_time>%s))' 
    param_values = [valid_date, valid_date, valid_time, airline_name, valid_date, valid_date, now_time]
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
    # query to get current flights
    # current flights classified as flights depart at most 2 hours before now() \
    # and that land after now() 
    cursor.execute(query,param_tuple)
    current = cursor.fetchall()
    cursor.close()

    available = True
    if len(current)<1:
        available = False

    return render_template('staff_current_flight.html', current = current, initial_src=src,
                            initial_dst=dst, available=available)

@app.route('/staff_past_flight')
def staff_past_flight():
    airline_name = session['airline_name']
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours=2)
    valid_date = valid_timestamp.date()
    now_time = timestamp.time()

    cursor = connection.cursor()
    # query to get past flight data
    # past flies classified as flights that landed before now()
    query = 'SELECT * FROM flight WHERE ((arrival_date<%s) OR (arrival_date=%s AND arrival_time<=%s))  \
            AND airline_name=%s'
    cursor.execute(query, (valid_date, valid_date, now_time, airline_name))
    past = cursor.fetchall()

    cursor.close()
    return render_template('staff_past_flight.html', past = past)

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
    return render_template('staff_view_flight.html')


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


@app.route('/go_add_flight')
def go_add_flight():
    return render_template('staff_add_flight.html')


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
    capacity = int(request.form['capacity'])
    ticket_count = int(request.form['ticket_count'])
    src_airport = request.form['src_airport']
    dst_airport = request.form['dst_airport']

    cursor = connection.cursor()

    query1 = 'select seats from airplane where airline_name=%s and plane_id=%s'
    cursor.execute(query1, (airline_name, plane_id))
    max_capacity = cursor.fetchone()
    # check plane exist, capacity constraints, and duplicate flight
    if max_capacity is None:
        message = 'Error: This Plane Does Not Exist !'
    else:
        if capacity > max_capacity['seats']:
            message = 'Error: Capacity Exceeded Max Capacity!'
        elif ticket_count > capacity:
            message = 'Error: Ticket Count Exceeded Capacity'
        else:
            query2 = 'select * from flight where airline_name=%s and flight_number=%s ' \
                     'and departure_date=%s and departure_time=%s'
            cursor.execute(query2, (airline_name, flight_number, departure_date, departure_time))
            the_flight = cursor.fetchone()
            if len(the_flight) != 0:
                message = 'Error: This Flight Already Exists!'
            else:
                query3 = 'insert into flight values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                cursor.execute(query3, (airline_name, flight_number, departure_date, departure_time, base_price,
                                        plane_id, status, capacity, ticket_count, arrival_date, arrival_time,
                                        src_airport, dst_airport))
                connection.commit()
                message = 'Plane Added Successfully'
    cursor.close()
    return render_template('staff_add_flight.html', message=message)


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
             'and departure_date=%s and departure_time=%s'
    cursor.execute(query1, (airline_name, flight_number, departure_date, departure_time))
    ticket = cursor.fetchone()
    if ticket is None:
        cursor.close()
        error = 'No Such Ticket or Flight Record'
        return render_template('staff_view_ratings.html', error=error)
    else:
        data = cursor.fetchall()
        avg = sum(data['rating'])/len(data['rating'])
        cursor.close()
        return render_template('staff_view_ratings.html', data=data, avg=avg, ticket=ticket)


@app.route('/go_view_reports')
def go_view_reports():
    return render_template('staff_view_reports.html')


@app.route('/view_reports', methods=['GET', 'POST'])
def view_reports():
    return


@app.route('/go_view_revenue')
def go_view_revenue():
    return render_template('staff_view_revenue.html')


@app.route('/view_revenue', methods=['GET', 'POST'])
def view_revenue():
    return


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