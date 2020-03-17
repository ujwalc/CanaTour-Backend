from flask import Flask, render_template, redirect, url_for, request
app = Flask(__name__)

@app.route("/")
def index():
    return render_template('buses.html')

@app.route("/home")
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)