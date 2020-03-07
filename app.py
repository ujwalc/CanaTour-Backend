from flask import Flask, render_template
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

@app.route("/source/city")
def database_connection():
	return render_template('index.html')

@app.route("/destination")
def database_connection():
	return render_template('index.html')

@app.route("/book/ticket")
def database_connection():
	return render_template('index.html')

@app.route("/get/report")
def database_connection():
	return render_template('index.html')

@app.route("/bus/schedule")
def database_connection():
	return render_template('index.html')

if __name__ == "__main__":
	app.run(debug=True)