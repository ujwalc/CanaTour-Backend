import psycopg2

def connection_manager():
	connection = psycopg2.connect(
	    database="postgres",
	    user="postgres",
	    password="postgres",
	    host="postgres.cviulopflptv.us-east-1.rds.amazonaws.com",
	    port='5432'
	)
	cursor=connection.cursor()
	return cursor