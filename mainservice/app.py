from flask import Flask, render_template, request, session, redirect
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
from datetime import date


app = Flask(__name__)
USER_POOL_ID = 'us-east-1_feVkMHrXA'
CLIENT_ID = '5fl0d45iue53026nou9fq3ppvh'
CLIENT_SECRET = ''
app.secret_key = "cloud assignment"

@app.route("/")
def home():
    user = ''
    if session.get('token_id'):
        user = session['token_id']
    return render_template('home.html',user=user)

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
    message = ''
    return render_template('login.html',message =message)

@app.route("/signout")
def signout():
    if session.get('token_id'):
        session['token_id'] = ''
        session['search_body'] = ''
    return render_template('home.html',user ='')

@app.route("/signin",methods=['POST','GET'])
def signin():
    device = 'web'
    if 'device'  in request.args:
        device = request.args['device']
    email = request.form['email']
    password = request.form['password']
    response = requests.get("http://127.0.0.1:3000/login/"+email+"/"+password)
    print(response)
    result = response.json()
    print(result)
    if result != '':
        session['token_id'] = email
    if result != '':
        if device != 'mobile':
            if session.get('search_body'):
                return redirect("http://127.0.0.1:5000/bus/search")
            else:
                return render_template('home.html',user=email)
        else:
            return json.dumps({"token_id":result,"username":email})
    else:
        return render_template('home.html',user='')

@app.route("/signup")
def signup():
	return render_template('signup.html')

@app.route("/user_signup",methods=['POST','GET'])
def user_signup():
    print("into signup")
    name = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirmpassword=request.form['confirmpassword']
    phonenumber=request.form['phonenumber']
    device = 'web'
    if 'device' in request.args:
        device = request.args['device']
    data = {'email':email,'password':password,'name':name,'phone_number':phonenumber}
    print(data)
    response = requests.post("http://127.0.0.1:3000/signup", json=data)
    print(response.json())
    session['email'] = response.json()
    if device != 'mobile':
        return redirect("http://127.0.0.1:5000/confirmsignupscreen")
    else:
        return True

@app.route("/confirmsignupscreen",methods=['POST','GET'])
def confirm_signupscreen():
    return render_template('signup_otp.html')

@app.route("/confirmsignup",methods=['POST','GET'])
def confirm_signup():
    user = ''
    if session.get('email'):
        user = session['email']
    print("into signup")
    otp = request.form['otp']
    device = 'web'
    if 'device' in request.args:
        device = request.args['device']
    data = {'email': user,'otp':otp}
    response = requests.post("http://127.0.0.1:3000/confirmsignup", json=data)
    print(response.json())
    if device != 'mobile':
        if response.json() == 'SUCCESS':
            session['token_id'] = user
            session['email'] = ''
            return render_template('home.html',user=user)
        else:
            session['email'] = ''
            return render_template('home.html', user=user)
    else:
        if response.json() == 'SUCCESS':
            return True
        else:
            return False


@app.route("/getallcities",methods=['GET'])
def getallcities():
    print(session.get('token_id'))
    if session.get('token_id'):
        user = session['token_id']
    else:
        user = ''
    destination_type=request.args['type']
    device = 'web'
    if 'device' in request.args:
        device = request.args['device']
    schd = connection.connection_manager()
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
        return render_template('home.html',source_list=source_cities,destination_list = destination_list,user=user)
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


@app.route("/book/ticket",methods=['POST','GET'])
def book_ticket():
    device = 'web'
    user = ''
    bus_dict = {}
    if 'device' in request.args:
        device = request.args['device']
    if 'user' in request.args:
        user = request.args['user']
    if session['token_id'] != '':
        user = session['token_id']
    if user != '':
        print(device)
        cardNumber = request.form['cardNumber']
        expityMonth = request.form['expiryMonth']
        expiryYear = request.form['expiryYear']
        cvCode = request.form['cvCode']
        number_of_travellers = session['search_body']['passengers']
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
        username = user
        data = {'cardNumber':cardNumber,'expiryMonth':expityMonth,'expiryYear':expiryYear,'cvCode':cvCode,'passengers':number_of_travellers,'scheduleid':scheduleid,'user':user}
        response = requests.post("http://127.0.0.1:5002/book/ticket",data=data)
        print(response)
        bus_dict = response.json()
        print(bus_dict)
        active_status = True
        return render_template('ticket.html',bus_dict=bus_dict,user=user)
    else:
        if device != 'mobile':
            return render_template('login.html')

@app.route("/payment")
def payment():
    message = ''
    if session.get('token_id'):
        user = session['token_id']
        price = int(request.args['price'])*int(session['search_body']['passengers'])
        session['scheduleid'] = request.args['id']
        print(price)
        return render_template('payment.html', price=price, user=user)
    else:
        message = 'Please Login in to Continue with your Booking'
        return render_template('login.html',message=message)

@app.route("/get/report", methods=['POST','GET'])
def get_report():
    if session.get('token_id'):
        token_id = session['token_id']
    device = 'web'
    if 'depdate' in request.form:
        dep_date = request.form['depdate']
    else:
        dep_date = date.today()
   #dep_date = request.form.get('depdate') # Fetching the date from the admin
    if dep_date != None:
        #busesdet_query = "select s.scheduleid, ct.sourcecityname, s.destid, d.destname, s.busid, s.journeydate, s.starttime, s.seatsavailable, s.price from schedule s, destination d, cities ct where s.destid=d.destid and s.sourcecityid=ct.sourcecityid and journeydate = '{}'".format(str(dep_date))
        travellers_query = "SELECT s.journeydate, d.destid, SUM(tk.seatsbooked) FROM schedule s, destination d, tickets tk WHERE s.scheduleid = tk.scheduleid AND s.destid=d.destid and s.journeydate = '{}' GROUP BY s.journeydate, d.destid".format(str(dep_date))
        
        # Establishing connection
        report_data = connection.connection_manager()

        # Extracting buses data
        #report_data.execute(busesdet_query)
        report_data.execute(
            "select s.scheduleid, ct.sourcecityname, s.destid, d.destname, s.busid, s.journeydate, s.starttime, s.seatsavailable, s.price from schedule s, destination d, cities ct where s.destid=d.destid and s.sourcecityid=ct.sourcecityid and journeydate = %s;",
            [dep_date])
        bus_res = report_data.fetchall()
        print(bus_res)
        all_bus_list = []

        for res in bus_res:
            bus_list = []
            bus_list.append(str(res[0]))
            bus_list.append(str(res[1]))
            bus_list.append(str(res[2]))
            bus_list.append(str(res[3]))
            bus_list.append(str(res[4]))
            bus_list.append(str(res[5]))
            bus_list.append(str(res[6]))
            bus_list.append(str(res[7]))
            bus_list.append(str(res[8]))

            all_bus_list.append(bus_list)

        # Extracting travellers data
        report_data.execute(travellers_query)
        trav_res = report_data.fetchall()
        
        all_trav_list = []

        for res in trav_res:
            trav_list = []
            trav_list.append(str(res[0]))
            trav_list.append(str(res[1]))
            trav_list.append(str(res[2]))
            print("JourneyDate: " + str(res[0]))
            print("Destination ID: " + str(res[1]))
            print("No. of travellers: " + str(res[2]))

            all_trav_list.append(trav_list)
        return render_template('report.html', all_bus_list=all_bus_list, all_trav_list=all_trav_list, dep_date=dep_date)
    else:
        return render_template('report.html')

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

@app.route("/bus/search",methods=['GET','POST'])
def get_schedule():
    print("into get bus search")
    if session.get('token_id'):
        user = session['token_id']
    else:
        user = ''
    bus_list = []
    device = 'web'
    if 'device' in request.args:
        device = request.args['device']
    if 'source' in request.form:
        session['search_body'] = ''
    if session.get('search_body'):
        print(session['search_body'])
        sourcecityid = session['search_body']['sourcecityid']
        destination_id = session['search_body']['destination_id']
        number_of_args = session['search_body']['passengers']
        journey_date = session['search_body']['journey_date']
    else:
        sourcecityid = request.form['source']
        destination_id = request.form['destination']
        number_of_args = request.form['passengers']
        journey_date = request.form['datepicker']
        #return_date = request.form['date2']
        session_dict = {}
        session_dict['sourcecityid'] = sourcecityid
        session_dict['destination_id'] = destination_id
        session_dict['journey_date'] = journey_date
        session_dict['passengers'] = number_of_args
        session['passengers'] = number_of_args
        session['search_body'] = session_dict
    print(sourcecityid,destination_id,number_of_args,journey_date)
    data = {'source': sourcecityid, 'destination': destination_id,'passengers':number_of_args,'datepicker':journey_date}
    response = requests.post("http://127.0.0.1:5001/bus/search", json=data)
    bus_list = response.json()['buslists']
    if device != 'mobile':
        return render_template('buses.html',bus_list=bus_list,user=user)
    else:
        return json.dumps({"buslists": bus_list})


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
	app.run(debug=True,host="0.0.0.0",port=5000)