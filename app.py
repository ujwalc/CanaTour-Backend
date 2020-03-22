from flask import Flask, render_template, request, session
import connection
import boto3
import requests
from boto3.session import Session
import botocore.exceptions
import hmac
import hashlib
import base64
import json
import psycopg2


app = Flask(__name__)
USER_POOL_ID = 'us-east-1_feVkMHrXA'
CLIENT_ID = '5fl0d45iue53026nou9fq3ppvh'
CLIENT_SECRET = ''
app.secret_key = "cloud assignment"

@app.route("/")
def home():
	return render_template('home.html')

@app.route("/check")
def database_connection():
	abc = connection.connection_manager()
	sql = """ 
	SELECT * FROM destination;
	"""
	abc.execute(sql)
	print(abc.fetchall())
	return render_template('index.html')

@app.route("/login")
def login():
	return render_template('login.html')

@app.route("/signin",methods=['POST'])
def signin():
    email = request.form['email']
    password = request.form['password']
    response = requests.get("http://127.0.0.1:3000/login/"+email+"/"+password)
    print(response)
    return render_template('home.html')

@app.route("/signup")
def signup():
	return render_template('signup.html')

@app.route("/source/city",methods=['GET'])
def check_source_city():
    if 'id' in request.args:
        id=request.args['id']
        abc = connection.connection_manager()
        sql = """SELECT * FROM cities WHERE cityid = ?"""
        abc.execute("SELECT sourcecityid,sourcecityname FROM cities WHERE sourcecityid = %s",[id])
        results = abc.fetchall()
        print(results)
        for res in results:
            cityname = res[1]
            cityid = res[0]
        return cityname+","+cityid
    else:
        print("Error")

@app.route("/getallcities",methods=['GET'])
def getallcities():
    destination_type=request.args['type']
    device = 'web'
    if 'device' in request.args:
        device = request.args['device']
    connection = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="postgres",
        host="cloud-database.c4tjyvon2isw.us-east-1.rds.amazonaws.com",
        port='5432'
    )
    schd = connection.cursor()
    sql = """SELECT * FROM cities WHERE cityid = ?"""
    schd.execute("SELECT sourcecityid,sourcecityname FROM cities")
    results = schd.fetchall()
    source_cities = []
    for res in results:
        source_dict = {'cityname': '', 'cityid': ''}
        source_dict['cityname'] = res[1]
        source_dict['cityid'] = res[0]
        source_cities.append(source_dict)
    print(source_cities)
    schd.execute("SELECT destid,destname FROM destination WHERE desttype = %s",[destination_type])
    results = schd.fetchall()
    destination_list = []
    for res in results:
        destination_dict = {}
        destination_dict['destname'] = res[1]
        destination_dict['destid'] =  res[0]
        destination_list.append(destination_dict)
    print(destination_list)
    if device != 'mobile':
        return render_template('home.html',source_list=source_cities,destination_list = destination_list)
    else:
        return json.dumps({"source_list": source_cities,"destination_list":destination_list})


@app.route("/destinations", methods=['GET'])
def check_destination():
    if 'id' in request.args:
        id = request.args['destonation_id']
        abc = connection.connection_manager()
        sql = """ 
			SELECT * FROM destinations_lookup WHERE cityid = ?
			"""
        abc.execute("SELECT cityid,cityname FROM cities_lookup WHERE cityid = %s", [id])
        results = abc.fetchall()
        for res in results:
            cityname = res[1]
            cityid = res[0]
    else:
        print("Error")
    return render_template('index.html')

@app.route("/destination")
def destination_search():
	return render_template('index.html')

@app.route("/book/ticket",methods=['POST','GET'])
def book_ticket():
    device = 'web'
    if 'device' in request.args:
        device = request.args['device']
    print(device)
    connection = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="postgres",
        host="cloud-database.c4tjyvon2isw.us-east-1.rds.amazonaws.com",
        port='5432'
    )
    schd = connection.cursor()
    # schd.execute("SELECT username FROM usersession")
    # session_dets = schd.fetchall()
    cardNumber = request.form['cardNumber']
    print(cardNumber)
    expityMonth = request.form['expiryMonth']
    expityYear = request.form['expiryYear']
    cvCode = request.form['cvCode']
    print(cvCode)
    number_of_travellers = 10
    if session.get('scheduleid'):
        scheduleid = session['scheduleid']
    else:
        if 'scheduleid' in request.args:
            scheduleid = request.args['scheduleid']
    if session.get('passengers'):
        passengers = session['passengers']
    else:
        if 'passengers' in request.args:
            passengers = request.args['passengers']
    username = 'vidip2'
    bus_dict = {}
    active_status = True
    if cardNumber == '1111111111111111' and expityYear > '19' and expityMonth > '03':
        print("into if")
        schd.execute("SELECT s.sourcecityid, s.destid, s.journeydate, s.starttime, s.busid, s.scheduleid,s.price FROM schedule s WHERE scheduleid = %s",[scheduleid])
        results = schd.fetchall()
        for res in results:
            bus_dict = {}
            source_city_id = res[0]
            destination_id = res[1]
            journeydate = res[2]
            starttime = res[3]
            busid = res[4]
            price= res[6]
            bus_dict['source_city_id'] = source_city_id
            bus_dict['destination_id'] = destination_id
            bus_dict['journeydate'] = journeydate
            bus_dict['starttime'] = starttime
            bus_dict['busid'] = busid
            bus_dict['scheduleid'] = res[5]
            bus_dict['price'] = res[6]
            bus_dict['username'] = username
            bus_dict['passengers'] = passengers
            print("Source City: " + source_city_id)
            print("Destination Name: " + destination_id)
            print("Bus start time: " + str(starttime))
            print("Bus id: " + str(busid))
        try:
            schd.execute(
                "INSERT INTO tickets (ticketid,username,destid,seatsbooked,active_status,scheduleid,payment) VALUES ('',%s,%s,%s,%s,%s,%s);",
                [destination_id,username,destination_id,number_of_travellers,active_status,scheduleid,bus_dict['price']])
            connection.commit()
        except Exception as e:
            print(e)
        print(bus_dict)
    else:
        print("into else")
    if device != 'mobile':
        return render_template('ticket.html',bus_dict=bus_dict)
    else:
        return bus_dict

@app.route("/payment")
def payment():
    price = request.args['price']
    session['scheduleid'] = request.args['id']
    print(price)
    return render_template('payment.html',price=price)

@app.route("/get/report")
def get_report():
	return render_template('index.html')

@app.route("/puts3")
def put_file_to_s3():
    print("hello")
    ACCESS_KEY = 'ASIA3JXAMQRQTK55UEUQ'
    SECRET_KEY = 'mQWeVUDwhgWYFN+FzffhOXgtrhiiHJInzZNJsIre'
    session = Session(aws_access_key_id = ACCESS_KEY, aws_secret_access_key = SECRET_KEY)
    s3 = session.resource('s3')
    buck = s3.Bucket('group4cloudproject')
    for b in buck.objects.all():
        print(b.key)
    return render_template('index.html')

@app.route("/bus/search",methods=['POST'])
def get_schedule():
    schd = connection.connection_manager()
    #schd.execute("SELECT username FROM usersession")
    #session_dets = schd.fetchall()
    sourcecityid = request.form['source']
    destination_id = request.form['destination']
    number_of_args = request.form['passengers']
    journey_date = request.form['datepicker']
    session['passengers'] = number_of_args
   # session['number_of_travllers'] = number_of_args
   # session['journey_date'] = journey_date
    print(sourcecityid,destination_id,number_of_args,journey_date)
#    for val in session_dets:
#        username = val[0]
#        print("Username: " + username)

    if 'destination' in request.form and 'source' in request.form and 'datepicker' in request.form and 'passengers' in request.form:
        schd.execute(
            "SELECT s.sourcecityid, s.destid, d.destname, d.destprov, s.journeydate, s.starttime, s.seatsavailable, s.busid, s.scheduleid,s.price FROM schedule s JOIN cities cl ON s.sourcecityid = cl.sourcecityid JOIN destination d ON d.destid = s.destid WHERE s.sourcecityid = %s AND s.destid = %s AND journeydate = %s;",
            [sourcecityid, destination_id,journey_date])
        results = schd.fetchall()
        print(results)
        bus_list = []
        for res in results:
            bus_dict = {}
            source_city_name = res[0]
            destination_name = res[2]
            destprov = res[3]
            journeydate = res[4]
            starttime = res[5]
            seatsavailable = res[6]
            busid = res[7]
            bus_dict['source_city_name'] = source_city_name
            bus_dict['destination_name'] = destination_name
            bus_dict['destprov'] = destprov
            bus_dict['journeydate'] = journeydate
            bus_dict['starttime'] = starttime
            bus_dict['seatsavailable'] = seatsavailable
            bus_dict['busid'] = busid
            bus_dict['scheduleid'] = res[8]
            bus_dict['price'] = res[9]
            print("Source City: " + source_city_name)
            print("Destination Name: " + destination_name)
            print("Destination Location: "+destprov)
            print("Bus start time: " + str(starttime))
            print("Seats Available: " + str(seatsavailable))
            print("Bus id: " + str(busid))
            bus_list.append(bus_dict)

    else:
        print("Error")
    return render_template('buses.html',bus_list=bus_list)

#def get_secret_hash(username):
#    msg = username + CLIENT_ID
#    dig = hmac.new(str(CLIENT_SECRET).encode('utf-8'),
#        msg = str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
#    d2 = base64.b64encode(dig).decode()
#    return d2


def initiate_auth(username,password):
    try:
        resp = client.admin_initiate_auth(
            UserPoolId=USER_POOL_ID,
            ClientId=CLIENT_ID,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
            'USERNAME':username,
            'SECRET_HASH':username,
            'PASSWORD':password
            },
        ClientMetaData={
        'username':username,
        'password':password
        })
    except client.exceptions.NotAuthorizedException as e:
        return None, "Username or password is incorrect"

@app.route("/checkcognito")
def lambda_handler():
    username = "vidip"
    email = "vidipmalhotra@gmail.com"
    password = "h123hello"
    name = "vidip"
    client = boto3.client('cognito-idp')
    response = client.list_users(
    UserPoolId=USER_POOL_ID,
    AttributesToGet=[
        'email',
    ],
    Limit=123
)
    return render_template('index.html')

if __name__ == "__main__":
	app.run(debug=True)