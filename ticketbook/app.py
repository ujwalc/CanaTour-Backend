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
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import smtplib
from email.message import EmailMessage


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
            host="postgres.cviulopflptv.us-east-1.rds.amazonaws.com",
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
                schd.execute(
                        "INSERT INTO tickets (username,destid,seatsbooked,active_status,scheduleid,payment) VALUES (%s,%s,%s,%s,%s,%s);",
                        [username,destination_id,int(number_of_travellers),active_status,int(scheduleid),bus_dict['price']])
                connection.commit()
                pdfName = username+str(1)
                pdfTitle = "Ticket Booking Success"
                bookingReference = 'Booking Reference: ' + str(1)
                name = 'Name: ' + username
                source = 'From: ' + source_city_id
                destination = 'To: ' + destination_id
                departureDay = 'Departure Day: ' + str(journeydate)
                departureTime = 'Departure Time: ' +str(starttime)
                numberOfTravellers = 'Number Of Travellers: ' + str(number_of_travellers)
                contactUs = 'Customer Support: canatour.mail@gmail.com'

                pdf = canvas.Canvas(pdfName)
                pdf.setTitle(pdfTitle)

                pdf.setFont("Helvetica-Bold",28)
                pdf.drawCentredString(280,800,'Travel Ticket')
                pdf.line(170, 790, 400, 790)

                pdf.setFont("Courier",14)
                pdf.drawString(50, 720, bookingReference)
                pdf.drawString(50, 700, name)
                pdf.drawString(50, 680, source)
                pdf.drawString(50, 660, destination)
                pdf.drawString(50, 640, departureDay)
                pdf.drawString(50, 620, departureTime)
                pdf.drawString(50, 600, numberOfTravellers)

                pdf.setFont("Courier-Bold",12)
                pdf.drawString(50, 100, contactUs)

                pdf.save()

                import smtplib
                from email.message import EmailMessage

                pdf_name = pdfName
                msg = EmailMessage()
                from_ = "canatour.mail@gmail.com"
                pwd = "canatour@123"
                msg['Subject'] = "Booking Successful - Canatour" 
                msg['From'] = from_
                msg['To'] = username
                msg.set_content('Please find attached your travel ticket. Hope you will enjoy the journey.')

                with open(pdf_name, 'rb') as f:
                    file_data = f.read()
                    file_name = f.name

                msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

                with smtplib.SMTP_SSL('smtp.gmail.com') as smtp:
                    smtp.login(from_,pwd)
                    smtp.send_message(msg)

            return bus_dict
        else:
            print("into else")
            return bus_dict
    else:
        return "No user logged in"


if __name__ == "__main__":
	app.run(debug=True,host="0.0.0.0",port=5002)