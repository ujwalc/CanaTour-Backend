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
app.secret_key = "cloud assignment"


@app.route("/bus/search",methods=['GET','POST'])
def get_schedule():
    print("into get bus search")
    schd = connection.connection_manager()
    sourcecityid = request.form['source']
    destination_id = request.form['destination']
    number_of_args = request.form['passengers']
    journey_date = request.form['datepicker']
   # session['number_of_travllers'] = number_of_args
   # session['journey_date'] = journey_date
    print(sourcecityid,destination_id,number_of_args,journey_date)
    bus_list = []
    if ('destination' in request.form and 'source' in request.form and 'datepicker' in request.form and 'passengers' in request.form) or session.get('search_body'):
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
            bus_dict['journeydate'] = str(journeydate)
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
    return json.dumps({"buslists": bus_list})

if __name__ == "__main__":
	app.run(debug=True,host="0.0.0.0",port=5001)