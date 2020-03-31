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
        new_dict = {}
        return json.dumps("all_bus_list":all_bus_list,"all_trav_list":all_trav_list,"dep_date":dep_date)
    else:
        return json.dumps("all_bus_list":all_bus_list,"all_trav_list":all_trav_list,"dep_date":dep_date)


if __name__ == "__main__":
	app.run(debug=True,host="0.0.0.0",port=5004)