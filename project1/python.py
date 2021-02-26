from flask import Flask, render_template, redirect, url_for, request, session
from flaskext.mysql import MySQL # had to wirte flaskext.mysql instead of flask-mysqldb
import MySQLdb.cursors
import MySQLdb as sql_db 
import re

import passlib
from passlib.hash import pbkdf2_sha256
#import requests




app = Flask(__name__)
app.secret_key = 'your secret key'
mysql = MySQL(app)


 
conn = sql_db.connect( 
	host='localhost', 
  	database='flaskdb', 
  	user='Jean', 
  	password='pierre') 




@app.route("/")
def main():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/register")
def register():
    return render_template('register.html')

@app.route('/testloginwithoutdb', methods=['GET', 'POST'])
def logintest():
    error = None
    greeting = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            greeting = request.form['username']
            return render_template('index.html', greeting=greeting)
            
    return render_template('index.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL

        hash = pbkdf2_sha256.hash(password)

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s ', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
        
        
            
        ok= pbkdf2_sha256.verify(account['password'], hash)
        print(account['password'])
        print(ok)
        # If account exists in accounts table in out database
        if account and pbkdf2_sha256.verify(account['password'], hash):
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = username
            # Redirect to home page 
            return render_template('index.html', msg=msg)
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


@app.route('/register', methods=['GET', 'POST'])
def registeruser():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table

            password = pbkdf2_sha256.hash(password)
           
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, email, password,))
            conn.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/myprofile')
def myprofile():

  if not session.get('loggedin'):
    return render_template('register.html')
  else:
    msg = session['username']  
    return render_template('myprofile.html', msg=msg)

@app.route('/logout')
def logout():

 if session.get('loggedin'):
    session['loggedin'] = False
    msg = "You have succesfully logged out"
    return render_template('index.html', msg=msg)

 else:
    msg = "Not logged in"
    return render_template('index.html', msg=msg)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=4000)

