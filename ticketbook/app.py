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
import time


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

@app.route("/get/bookinghistory", methods=['GET'])
def get_booking_history():
    connection = psycopg2.connect(
            database="postgres",
            user="postgres",
            password="postgres",
            host="postgres.cviulopflptv.us-east-1.rds.amazonaws.com",
            port='5432'
    )

    b_history = connection.cursor()
    new_dict = {}
    emailid = request.args['user']
    print(emailid)
    userdet_query = "select ud.firstname, ud.lastname from userdetails ud where ud.emailid='{}'".format(str(emailid))
    if emailid != '':
        b_history.execute(userdet_query)
        user_det = b_history.fetchall()
        for res in user_det:
            firstname = res[0]
            lastname = res[1]
        book_history_query = "select  tk.ticketid, ct.sourcecityname, d.destname, d.destprov, s.journeydate, s.starttime, tk.seatsbooked, tk.payment, ud.firstname, ud.lastname from tickets tk, schedule s, cities ct, destination d, userdetails ud where tk.emailid=ud.emailid and tk.scheduleid=s.scheduleid and tk.destid=d.destid and s.sourcecityid=ct.sourcecityid and tk.emailid='{}' order by s.journeydate desc".format(str(emailid))
        b_history.execute(book_history_query)
        book_history_res = b_history.fetchall()
        all_book_history = []
        for res in book_history_res:
            bk_hist_list = []
            bk_hist_list.append(str(res[0]))
            bk_hist_list.append(str(res[1]))
            bk_hist_list.append(str(res[2]))
            bk_hist_list.append(str(res[3]))
            bk_hist_list.append(str(res[4]))
            bk_hist_list.append(str(res[5]))
            bk_hist_list.append(str(res[6]))
            bk_hist_list.append(str(res[7]))
            bk_hist_list.append(str(res[8]))
            bk_hist_list.append(str(res[9]))
            all_book_history.append(bk_hist_list)
        new_dict['emailid'] = emailid
        new_dict['firstname'] = firstname
        new_dict['lastname'] = lastname
        new_dict['all_book_history']=all_book_history
        return new_dict
    else:
        return new_dict



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
                booking_time = int(time.time())
                schd.execute(
                        "INSERT INTO tickets (emailid,destid,seatsbooked,active_status,scheduleid,payment,booking_time) VALUES (%s,%s,%s,%s,%s,%s,%s);",
                        [username,destination_id,int(number_of_travellers),active_status,int(scheduleid),bus_dict['price'],booking_time])
                connection.commit()
                schd.execute(
                        "UPDATE schedule SET seatsavailable = seatsavailable - %s WHERE scheduleid = %s",
                        [int(number_of_travellers),int(scheduleid)])
                connection.commit()
                ticket_query = "select tk.ticketid, ud.firstname, ud.lastname, ud.emailid, ct.sourcecityname, d.destname, d.destprov, s.journeydate, s.starttime, tk.seatsbooked, tk.payment from userdetails ud, tickets tk, destination d, schedule s, cities ct where ud.emailid=tk.emailid and tk.destid=d.destid and tk.scheduleid=s.scheduleid and s.sourcecityid=ct.sourcecityid and tk.emailid='{}' order by booking_time desc Limit 1".format(username)

                schd.execute(ticket_query)
                ticket_results = schd.fetchall()

                for res in ticket_results:
                    pdf_ticketid = str(res[0])
                    pdf_name = str(res[1])
                    pdf_email = str(res[3])
                    pdf_source = str(res[4])
                    pdf_dest = str(res[5])+", "+str(res[6])
                    pdf_departure_date = str(res[7])
                    pdf_departure_time = str(res[8])
                    pdf_seatsbooked = str(res[9])
                    pdf_payment = "$"+str(res[10])
                
                pdfName = username.split('@')[0]+'_'+pdf_ticketid+'_ticket.pdf'
                pdfTitle = "Hi "+pdf_name+"! Here's your ticket."
                bookingReference = 'Ticket ID#: ' + pdf_ticketid
                name = 'Email: ' + pdf_email
                source = 'From: ' + pdf_source
                destination = 'To: ' + pdf_dest
                departureDay = 'Departure Day: ' + pdf_departure_date
                departureTime = 'Departure Time: ' + pdf_departure_time
                numberOfTravellers = 'Number Of Travellers: ' + pdf_seatsbooked
                amount_paid = 'Amount paid: '+pdf_payment
                contactUs = 'Customer Support: canatour.mail@gmail.com'

                pdf = canvas.Canvas(pdfName)
                pdf.setTitle(pdfTitle)

                pdf.setFont("Helvetica-Bold",28)
                pdf.drawCentredString(280,800,'Travel Ticket')
                pdf.line(170, 790, 400, 790)

                pdf.setFont("Courier",14)
                pdf.drawString(50, 740, pdfTitle)
                pdf.drawString(50, 720, bookingReference)
                pdf.drawString(50, 700, name)
                pdf.drawString(50, 680, source)
                pdf.drawString(50, 660, destination)
                pdf.drawString(50, 640, departureDay)
                pdf.drawString(50, 620, departureTime)
                pdf.drawString(50, 600, numberOfTravellers)
                pdf.drawString(50, 580, amount_paid)
                pdf.setFont("Courier-Bold",12)
                pdf.drawString(50, 100, contactUs)

                pdf.save()
                pdf_name = pdfName
                msg = EmailMessage()
                from_ = "canatour.mail@gmail.com"
                pwd = "canatour@123"
                msg['Subject'] = "Booking Successful - Canatour" 
                msg['From'] = from_
                msg['To'] = username
                msg.set_content('Please find attached your travel ticket. Hope you enjoy the journey.')

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