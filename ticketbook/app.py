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


@app.route("/book/ticket",methods=['POST','GET'])
def book_ticket():
    connection = psycopg2.connect(
            database="postgres",
            user="postgres",
            password="postgres",
            host="cloud-database.c4tjyvon2isw.us-east-1.rds.amazonaws.com",
            port='5432'
    )
    schd = connection.cursor()
    cardNumber = request.form['cardNumber']
    expiryMonth = request.form['expiryMonth']
    expiryYear = request.form['expiryYear']
    cvCode = request.form['cvCode']
    number_of_travellers = request.form['passengers']
    scheduleid = request.form['scheduleid']
    username = request.form['user']
    bus_dict = {}
    active_status = True
    if username != '':
        if cardNumber == '1111111111111111' and expiryYear > '19' and expiryMonth > '03':
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
                bus_dict['price'] = int(res[6])*int(number_of_travellers)
                bus_dict['username'] = username
                bus_dict['passengers'] = number_of_travellers
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
            return bus_dict
        else:
            print("into else")
            return bus_dict
    else:
        return "No user logged in"


if __name__ == "__main__":
	app.run(debug=True,host="0.0.0.0",port=5002)