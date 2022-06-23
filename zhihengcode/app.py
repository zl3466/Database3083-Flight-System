import pymysql.cursors, hashlib
from flask import Flask, render_template, request, session, url_for, redirect
from datetime import timedelta, datetime

app = Flask(__name__)

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='',
                       db='blog',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


# Define route for login
@app.route('/login')
def login():
    return render_template('login.html')


# Define route for register
@app.route('/register')
def register():
    return render_template('register.html')


# ---------------------------------PUBLIC-------------------------------------------
@app.route('/public_home')
def public_home():
    return render_template('public_home.html')


@app.route('/public_oneway')
def public_oneway():
    return render_template('public_viewflight.html')


@app.route('/public_rt')
def public_rt():
    return render_template('public_viewflight.html', round_trip=True)


@app.route('/public_view_flight')
def public_view_flight():
    # declaring timestamp for now
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours=2)
    valid_time = valid_timestamp.time()
    valid_date = valid_timestamp.date()
    cursor = conn.cursor()
    # query to get all upcoming flight data
    query = 'SELECT * FROM flight WHERE (departure_date>%s) OR (departure_date=%s and departure_time>%s)'
    cursor.execute(query, (valid_date, valid_date, valid_time))
    data = cursor.fetchall()
    cursor.close()
    return render_template('public_viewflight.html', data=data)


@app.route('/public_search_flight')
def public_search_flight():
    param_dict = {}
    param_dict['src_name'] = request.form['src_name']
    param_dict['dst_name'] = request.form['dst_name']
    param_dict['departure_date'] = request.form['departure_date']
    param_dict['departure_time'] = request.form['departure_time']
    query = "SELECT * FROM flight"
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
    cursor = conn.cursor()
    cursor.execute(search, param_tuple)
    data = cursor.fetchall()
    cursor.close()
    return render_template('public_searchflight.html', data=data)


@app.route('/public_search_flight_rt')
def public_search_flight_rt():
    # dictionary for search parameters
    param_dict = {}
    param_dict['src_name'] = request.form['src_name']
    param_dict['dst_name'] = request.form['dst_name']
    param_dict['departure_date'] = request.form['departure_date']
    param_dict['departure_time'] = request.form['departure_time']
    # dictionary for return search parameters
    param_dictRT = {}
    param_dictRT['dst_name'] = request.form['src_name']
    param_dictRT['src_name'] = request.form['dst_name']
    param_dictRT['departure_date'] = request.form['return_date']
    param_dictRT['departure_time'] = request.form['return_time']

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
    cursor = conn.cursor()
    cursor.execute(search, param_tuple)
    data = cursor.fetchall()
    cursor.close()
    return render_template('public_searchflight.html', data=data, roundtrip=True)


# ---------------------------------CUSTOMER-------------------------------------------
@app.route('/customer_home')
def customer_home():
    email = session['email']
    cursor = conn.cursor()
    query = 'SELECT name FROM customer WHERE email=%s'
    cursor.execute(query, email)
    name = cursor.fetchone()
    return render_template('customer_home.html', name=name)


@app.route('/customer_oneway')
def customer_oneway():
    return render_template('customer_searchflight.html')


@app.route('/customer_rt')
def customer_rt():
    return render_template('customer_searchflight.html', round_trip=True)


@app.route('/customer_search_flight')
def customer_search_flight():
    param_dict = {}
    param_dict['src_name'] = request.form['src_name']
    param_dict['dst_name'] = request.form['dst_name']
    param_dict['departure_date'] = request.form['departure_date']
    param_dict['departure_time'] = request.form['departure_time']
    query = "SELECT * FROM flight"
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
    cursor = conn.cursor()
    cursor.execute(search, param_tuple)
    data = cursor.fetchall()
    cursor.close()
    return render_template('customer_searchflight.html', data=data)


@app.route('/customer_search_flight_rt')
def customer_search_flight_rt():
    # dictionary for search parameters
    param_dict = {}
    param_dict['src_name'] = request.form['src_name']
    param_dict['dst_name'] = request.form['dst_name']
    param_dict['departure_date'] = request.form['departure_date']
    param_dict['departure_time'] = request.form['departure_time']
    # dictionary for return search parameters
    param_dictRT = {}
    param_dictRT['dst_name'] = request.form['src_name']
    param_dictRT['src_name'] = request.form['dst_name']
    param_dictRT['departure_date'] = request.form['return_date']
    param_dictRT['departure_time'] = request.form['return_time']

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
    cursor = conn.cursor()
    cursor.execute(search, param_tuple)
    data = cursor.fetchall()
    cursor.close()
    return render_template('customer_searchflight.html', data=data, roundtrip=True)


# unfinished purchase()
@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    username = session['username']
    cursor = conn.cursor()
    airline_name = request.form['airline_name']
    flight_number = request.form['flight_number']
    departure_date = request.form['departure_date']
    departure_time = request.form['departure_time']

    query1 = 'select max(ticket_id) from ticket'
    cursor.execute(query1)
    last_ticket_id = cursor.fetchone()
    new_ticket_id = last_ticket_id + 1

    query2 = 'insert into ticket (ticket_id, airline_name, flight_number, departure_date, departure_time, sold_price) ' \
             'values (%s, %s, %s, %s, %s, %s)'
    cursor.execute(query2, (airline_name, flight_number, departure_date, departure_time,))
    conn.commit()
    cursor.close()
    return redirect(url_for('home'))


@app.route('/my_flight', methods=['GET', 'POST'])
def my_flight():
    email = session['email']
    cursor = conn.cursor()
    query = 'select * from ticket where email=%s'
    cursor.execute(query, email)
    data = cursor.fetchall()
    for line in data:
        session[line['ticket_id']] = line['ticket_id']
    cursor.close()
    return render_template('my_flights.html', data=data)


# unfinished cancel_flight()
@app.route('/cancel_flight', methods=['GET', 'POST'])
def cancel_flight():
    return


# ---------------------------------STAFF-------------------------------------------
@app.route('/staff_home')
def staff_home():
    username = session['username']
    cursor = conn.cursor()
    query1 = 'SELECT first_name FROM staff WHERE username=%s'
    cursor.execute(query1, username)
    first_name = cursor.fetchone()
    query2 = 'SELECT airline_name FROM staff WHERE username=%s'
    cursor.execute(query2, username)
    airline_name = cursor.fetchone()
    return render_template('customer_home.html', first_name=first_name, airline_name=airline_name)
    return render_template('staff_home.html')


@app.route('/staff_view_flight')
def staff_view_flight():
    # declaring timestamp for now
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours=2)
    valid_time = valid_timestamp.time()
    valid_date = valid_timestamp.date()
    cursor = conn.cursor()
    # query to get all upcoming flight data
    query = 'SELECT * FROM flight WHERE (departure_date>%s) OR (departure_date=%s and departure_time>%s)'
    cursor.execute(query, (valid_date, valid_date, valid_time))
    data = cursor.fetchall()
    cursor.close()
    return render_template('staff_viewflight.html', data=data)


@app.route('/staff_search_flight')
def staff_search_flight():
    param_dict = {}
    param_dict['departure_date'] = request.form['departure_date']
    param_dict['departure_time'] = request.form['departure_time']
    query = "SELECT * FROM flight"
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
    cursor = conn.cursor()
    cursor.execute(search, param_tuple)
    data = cursor.fetchall()
    cursor.close()
    return render_template('staff_viewflight.html', data=data)


# unfinished change_status()
@app.route('/change_status')
def change_status():
    new_status = request.form['change_status']
    if new_status != 'null':
        cursor = conn.cursor()
        query = 'update flight set status=%s where '
        cursor.execute(query, new_status)
        conn.commit()
        cursor.close()
    return


@app.route('/add_plane')
def go_add_plane():
    return render_template('add_plane.html')


@app.route('/add_flight')
def go_add_flight():
    return render_template('add_flight.html')


@app.route('/add_airport')
def add_airport():
    return


@app.route('/view_ratings')
def view_ratings():
    return


@app.route('/view_reports')
def view_reports():
    return


@app.route('/view_revenue')
def view_revenue():
    return


@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    identity = request.form['user_type']

    # if customer register
    if identity == 'customer':
        email = request.form['email']
        password = request.form['password']
        # hashing passwrod with md5
        password = hashlib.md5(password.encode('utf-8')).hexdigest()
        cursor = conn.cursor()
        # query to get data on registering user
        query = 'SELECT * FROM customer WHERE email = %s'
        cursor.execute(query, (email))
        data = cursor.fetchone()

        # case: user data in database --> throw error
        if (data):
            return render_template('register.html', error="This user already exists")
        else:
            # case: user data not in database --> insert new user data
            ins = 'INSERT INTO customer(email, password) VALUES(%s, %s)'
            cursor.execute(ins, (email, password))
            conn.commit()
            cursor.close()
            return render_template('index.html')
    # elif staff register
    else:
        username = request.form['username']
        password = request.form['password']
        password = hashlib.md5(password.encode('utf-8')).hexdigest()
        cursor = conn.cursor()
        query = 'SELECT * FROM staff WHERE username = %s'
        cursor.execute(query, (username))
        data = cursor.fetchone()

        if (data):
            error = "This user already exists"
            return render_template('register.html', error=error)
        else:
            ins = 'INSERT INTO staff(username, password) VALUES(%s, %s)'
            cursor.execute(ins, (username, password))
            conn.commit()
            cursor.close()
            return render_template('index.html')


@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    identity = request.form['user_type']

    # if customer login
    if identity == 'customer':
        email = request.form['email']
        password = request.form['password']
        password = hashlib.md5(password.encode('utf-8')).hexdigest()

        cursor = conn.cursor()
        query = 'SELECT password FROM customer WHERE username = %s'
        cursor.execute(query, (email))
        data = cursor.fetchone()
        cursor.close()
        if (data):
            # checking password
            if data['password'] == password:
                # setting session to current user
                session['email'] = email
                return redirect(url_for('cust_home'))
            # case: password does not match --> throw error
            else:
                return render_template('login.html', error="Incorrect password")
        else:
            return render_template('login.html', error="Invalid username")

    # elif staff login
    else:
        username = request.form['username']
        password = request.form['password']
        password = hashlib.md5(password.encode('utf-8')).hexdigest()

        cursor = conn.cursor()
        query = 'SELECT password FROM staff WHERE username = %s'
        cursor.execute(query, (username))
        data = cursor.fetchone()
        cursor.close()
        if (data):
            if data['password'] == password:
                session['username'] = username
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error="Incorrect password")
        else:
            return render_template('login.html', error="Invalid username")


if __name__ == '__main__':
    app.run()
