from flask import Flask, render_template, request
import connection
import boto


app = Flask(__name__)

@app.route("/")
def hello():
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
			cityid = res[0]
	else:
		print("Error")

	return render_template('index.html')

@app.route("/destination")
def destination_search():
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