import pymysql.cursors, hashlib
from flask import Flask, render_template, request, session, url_for, redirect
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

app = Flask(__name__)

conn = pymysql.connect(host='localhost',
                       user='root',
                       port=8889,
                       password='root',
                       db='flight_system_db',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

app.secret_key = 'some key that you will never guess'

@app.route('/')
def index():  # put application's code here
    return render_template('index.html')


# ---------------------------------LOGIN-------------------------------------------
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/customer_login')
def customer_login():
    return render_template('login.html', user_type='customer')


@app.route('/staff_login')
def staff_login():
    return render_template('login.html', user_type='staff')


@app.route('/customer_loginAuth', methods=['GET', 'POST'])
def customer_loginAuth():
    email = request.form['email']
    password = request.form['password']
    password = hashlib.md5(password.encode('utf-8')).hexdigest()

    cursor = conn.cursor()
    query = 'SELECT password FROM customer WHERE email = %s'
    cursor.execute(query, email)
    data = cursor.fetchone()

    cursor.close()
    if data:
        # checking password (encoded)
        if hashlib.md5(data['password'].encode('utf-8')).hexdigest() == password:
            # setting session to current user
            session['email'] = email
            return redirect(url_for('customer_home'))
        # case: password does not match --> throw error
        else:
            return render_template('login.html', error="Incorrect password")
    else:
        return render_template('login.html', error="Invalid username")


@app.route('/staff_loginAuth', methods=['GET', 'POST'])
def staff_loginAuth():
    username = request.form['username']
    password = request.form['password']
    password = hashlib.md5(password.encode('utf-8')).hexdigest()

    cursor = conn.cursor()
    query = 'SELECT password FROM staff WHERE username = %s'
    cursor.execute(query, username)
    data = cursor.fetchone()
    query2 = 'SELECT airline_name FROM staff WHERE username=%s'
    cursor.execute(query2, username)
    airline_name = cursor.fetchone()['airline_name']
    cursor.close()
    if data:
        if hashlib.md5(data['password'].encode('utf-8')).hexdigest() == password:
            session['username'] = username
            session['airline_name'] = airline_name
            return redirect(url_for('staff_home'))
        else:
            return render_template('login.html', error="Incorrect password")
    else:
        return render_template('login.html', error="Invalid username")


# ---------------------------------REGISTER-------------------------------------------
@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/customer_register')
def customer_register():
    return render_template('register.html', user_type='customer')


@app.route('/staff_register')
def staff_register():
    return render_template('register.html', user_type='staff')


@app.route('/customer_registerAuth', methods=['GET', 'POST'])
def customer_registerAuth():
    email = request.form['email']
    password = request.form['password']
    # hashing passwrod with md5
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    cursor = conn.cursor()
    # query to get data on registering user
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, email)
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


@app.route('/staff_registerAuth', methods=['GET', 'POST'])
def staff_registerAuth():
    username = request.form['username']
    password = request.form['password']
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    cursor = conn.cursor()
    query = 'SELECT * FROM staff WHERE username = %s'
    cursor.execute(query, username)
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


# ---------------------------------PUBLIC-------------------------------------------
@app.route('/public_home')
def public_home():
    return render_template('public_home.html')


@app.route('/public_oneway')
def public_oneway():
    return render_template('public_view_flight.html')


@app.route('/public_rt')
def public_rt():
    return render_template('public_view_flight.html', round_trip=True)


@app.route('/public_view_flight', methods=['GET', 'POST'])
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
    return render_template('public_view_flight.html', data=data)


@app.route('/public_view_status')
def public_view_status():
    return render_template('public_check_status.html')


@app.route('/public_check_status', methods=['GET', 'POST'])
def public_check_status():
    airline_name = request.form['airline_name']
    flight_number = request.form['flight_number']
    departure_date = request.form['departure_date']
    departure_time = request.form['departure_time']
    cursor = conn.cursor()
    query = 'SELECT * FROM flight WHERE airline_name=%s and flight_number=%s and departure_date=%s and departure_time=%s'
    cursor.execute(query, (airline_name, flight_number, departure_date, departure_time))
    data = cursor.fetchall()
    cursor.close()
    return render_template('public_check_status.html', data=data)


@app.route('/public_search_flight', methods=['GET', 'POST'])
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


@app.route('/public_search_flight_rt', methods=['GET', 'POST'])
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
@app.route('/customer_home', methods=['GET', 'POST'])
def customer_home():
    email = session['email']
    cursor = conn.cursor()
    query = 'SELECT name FROM customer WHERE email=%s'
    cursor.execute(query, email)
    name = cursor.fetchone()['name']
    return render_template('customer_home.html', name=name)


@app.route('/customer_oneway')
def customer_oneway():
    return render_template('customer_search_flight.html')


@app.route('/customer_rt')
def customer_rt():
    return render_template('customer_search_flight.html', round_trip=True)


@app.route('/customer_search_flight', methods=['GET', 'POST'])
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
    return render_template('customer_search_flight.html', data=data)


@app.route('/customer_search_flight_rt', methods=['GET', 'POST'])
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
    return render_template('customer_search_flight.html', data=data, roundtrip=True)


@app.route('/my_flight', methods=['GET', 'POST'])
def my_flight():
    email = session['email']
    cursor = conn.cursor()
    query = 'select * from ticket where email=%s'
    cursor.execute(query, email)
    data = cursor.fetchall()
    cursor.close()
    return render_template('customer_my_flights.html', data=data)


@app.route('/cancel_flight', methods=['GET', 'POST'])
def cancel_flight():
    ticket_id = request.form['ticket_id']
    cursor = conn.cursor()
    # query = 'delete from ticket where ticket_id=%s'
    query = 'update ticket set card_type=%s, card_number=%s, exp_date=%s, purchase_date=%s, purchase_time=%s, email=%s ' \
            'where ticket_id=%s'
    cursor.execute(query, (None, None, None, None, None, None, ticket_id))
    conn.commit()
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
    cursor = conn.cursor()

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
    cursor = conn.cursor()

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
    cursor = conn.cursor()

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
    print(data['airline_name'])
    print(data['flight_number'])
    return render_template('purchase.html', data=data)


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

    cursor = conn.cursor()

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
    print((new_ticket_id, card_type, card_number, card_name, exp_date, valid_date,
                            valid_time, email, airline_name, flight_number, departure_date, departure_time, base_price))

    query2 = 'insert into ticket (ticket_id, card_type, card_number, card_name, exp_date, purchase_date, ' \
             'purchase_time, email, airline_name, flight_number, departure_date, departure_time, sold_price)' \
             'values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    cursor.execute(query2, (new_ticket_id, card_type, card_number, card_name, exp_date, valid_date,
                            valid_time, email, airline_name, flight_number, departure_date, departure_time, base_price))
    conn.commit()
    cursor.close()
    return render_template('customer_search_flight.html')


# ---------------------------------STAFF-------------------------------------------
@app.route('/staff_home', methods=['GET', 'POST'])
def staff_home():
    username = session['username']
    cursor = conn.cursor()
    query1 = 'SELECT first_name FROM staff WHERE username=%s'
    cursor.execute(query1, username)
    first_name = cursor.fetchone()['first_name']
    airline_name = session['airline_name']
    return render_template('staff_home.html', first_name=first_name, airline_name=airline_name)


@app.route('/staff_view_flight', methods=['GET', 'POST'])
def staff_view_flight():
    # declaring timestamp for now
    timestamp = datetime.now()
    valid_timestamp = timestamp + timedelta(hours=2)
    valid_time = valid_timestamp.time()
    valid_date = valid_timestamp.date()
    cursor = conn.cursor()
    airline_name = session['airline_name']
    # query to get all upcoming flight data
    query = 'SELECT * FROM flight WHERE ((departure_date>%s) OR (departure_date=%s and departure_time>%s)) ' \
            'and airline_name=%s'
    cursor.execute(query, (valid_date, valid_date, valid_time, airline_name))
    data = cursor.fetchall()
    cursor.close()
    return render_template('staff_view_flight.html', data=data)


@app.route('/staff_search_flight', methods=['GET', 'POST'])
def staff_search_flight():
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    query = "SELECT * FROM flight where airline_name=%s and ((departure_date>%s and departure_date<%s) " \
            "or departure_date=%s or departure_date=%s)"
    cursor = conn.cursor()
    cursor.execute(query, (session['airline_name'], start_date, end_date, start_date, end_date))
    data = cursor.fetchall()
    cursor.close()
    return render_template('staff_view_flight.html', data=data)


# unfinished change_status()
@app.route('/change_status', methods=['GET', 'POST'])
def change_status():
    new_status = request.form['status']
    airline_name = session['airline_name']
    flight_number = request.form['flight_number']
    departure_date = request.form['departure_date']
    departure_time = request.form['departure_time']
    if new_status is not None:
        cursor = conn.cursor()
        query = 'update flight set status=%s where airline_name=%s and flight_number=%s ' \
                'and departure_date=%s and departure_time=%s'
        cursor.execute(query, (new_status, airline_name, flight_number, departure_date, departure_time))
        conn.commit()
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
    cursor = conn.cursor()
    query1 = 'select * from airplane where plane_id=%s'
    cursor.execute(query1, plane_id)
    plane = cursor.fetchone()
    if plane is not None:
        message = 'Error: Plane Already Exist!'
    else:
        query2 = 'insert into airplane values(%s, %s, %s, %s, %s)'
        cursor.execute(query2, (airline_name, plane_id, seat_num, manufacturer, age))
        conn.commit()
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

    cursor = conn.cursor()

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
                conn.commit()
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

    cursor = conn.cursor()

    query1 = 'select * from airport where name=%s'
    cursor.execute(query1, name)
    duplicate = cursor.fetchone()
    if duplicate is not None:
        message = 'This Airport Already Exist in System'
    else:
        query2 = 'insert into airport values(%s, %s, %s, %s)'
        cursor.execute(query2, (name, city, country, type))
        conn.commit()
        message = 'Airport Added Successfully'
    cursor.close()
    return render_template('staff_add_airport.html', message=message)


@app.route('/view_ratings')
def view_ratings():
    return


@app.route('/view_reports')
def view_reports():
    return


@app.route('/view_revenue')
def view_revenue():
    return




if __name__ == '__main__':
    app.run('127.0.0.1', 5000, debug = True)
