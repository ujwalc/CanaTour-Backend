from flask import Flask, render_template, request
import connection
import boto


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

@app.route("/destination")
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

@app.route("/bus/schedule")
def get_schedule():
	return render_template('index.html')

@app.route("/sendfiletos3")
def put_file_to_s3():
	conn = S3Connection('<aws access key>', '<aws secret key>')
	return render_template('index.html')

if __name__ == "__main__":
	app.run(debug=True)