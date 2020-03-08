from flask import Flask, render_template, request
import connection
import boto
from datetime import datetime


app = Flask(__name__)

@app.route("/")
def hello():
	print("Hello")
	return render_template('index.html')

@app.route("/check")
def database_connection():
	abc = connection.connection_manager()
	sql = """ 
	SELECT * FROM destination;
	"""
	abc.execute(sql)
	print(abc.fetchall())
	return render_template('index.html')

@app.route("/source/city",methods=['GET'])
def check_source_city():
	if 'id' in request.args:
		id=request.args['id']
		abc = connection.connection_manager()
		sql = """ 
		SELECT * FROM cities_lookup WHERE cityid = ?
		"""
		abc.execute("SELECT cityid,cityname FROM cities_lookup WHERE cityid = %s",[id])
		results = abc.fetchall()
		for res in results:
			cityname = res[1]
			print(cityname)
			cityid = res[0]
			print(cityid)
	else:
		print("Error")

	return render_template('index.html')

@app.route("/destination",methods=['GET'])
def destination_search():
	if 'id' in request.args:
		id=request.args['id']
		dest_srch = connection.connection_manager()
		dest_srch.execute("select destid, destname, destdesc, destloc, destprov from destination where desttype= %s",[id])
		results = dest_srch.fetchall()
		for res in results:
			destid = res[0]
			destname = res[1]
			destdesc = res[2]
			destloc = res[3]+', '+res[4]
			destprov = res[4]

			print(destid)
			print(destname)
			print(destdesc)
			print(destloc)
			print(destprov)
			print('\n')
	else:
		print("Error")
	return render_template('index.html')

@app.route("/book/ticket")
def book_ticket():
	return render_template('index.html')

@app.route("/get/report")
def get_report():
	return render_template('index.html')

@app.route("/bus/schedule",methods=['GET']) # For this Function, we already assume that the username is stored in 'usersession' table, and the user source city is directly picked from there.
def get_schedule():
	schd = connection.connection_manager()
	schd.execute("SELECT username FROM usersession")
	session_dets = schd.fetchall()

	for val in session_dets:
		username = val[0]
		print ("Username: "+username)

	if 'dest' in request.args:
		destination=request.args['dest']
		
		schd.execute("SELECT s.sourcecity, s.destid, d.destname, d.destloc, d.destprov, s.journeydate, s.starttime, s.seatsavailable FROM schedule s, usersession us, cities_lookup cl, destination d WHERE us.usersourcecity = cl.cityid AND cl.cityname=s.sourcecity AND d.destid=s.destid AND s.destid = %s AND us.username= %s",[destination,username])
		results = schd.fetchall()

		for res in results:
			srccity = res[0]
			destid = res[1]
			destname = res[2]
			destloc = res[3]
			destprov = res[4]
			journeydate = res[5]
			starttime = res[6]
			seatsav = res[7]

			jourdate=journeydate.strftime("%m-%d-%Y")

			print("Source City: "+srccity)
			print("Destination Name: "+destname)
			print("Destination Location: "+destloc+', '+destprov)
			print("Date of journey: "+jourdate)
			print("Bus start time: "+starttime)
			print("Seats Available: "+str(seatsav))
	else:
		print("Error")
	return render_template('index.html')

@app.route("/sendfiletos3")
def put_file_to_s3():
	conn = S3Connection('<aws access key>', '<aws secret key>')
	return render_template('index.html')

if __name__ == "__main__":
	app.run(debug=True)