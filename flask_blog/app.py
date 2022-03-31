from flask import Flask, flash, render_template, request, redirect, url_for, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import urllib.request
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:lili@localhost/logindb'

db = SQLAlchemy(app)

app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'lili'
app.config['MYSQL_DB'] = 'logindb' 
  

class logindb(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    subtitle = db.Column(db.String(50))
    author = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    content = db.Column(db.Text)

mysql = MySQL(app)

@app.route('/')
def index():
    posts = logindb.query.order_by(logindb.date_posted.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
        else:
            msg = 'Incorrect username / password !'
    return render_template('add.html', msg = msg)


  
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
  

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form  :
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'

        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s)', (username, password, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
            return render_template('login.html')
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/post/<int:post_id>')
def post(post_id):
    post = logindb.query.filter_by(id=post_id).one()
    return render_template('post.html', post=post)

@app.route('/add')
def add():
    return render_template('login.html')


@app.route('/addpost', methods=['POST'])
def addpost():
    title = request.form['title']
    subtitle = request.form['subtitle']
    author = request.form['author']
    content = request.form['content']

    post = logindb(title=title, subtitle=subtitle, author=author, content=content, date_posted=datetime.now())

    db.session.add(post)
    db.session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
    

    #return render_template('add.html')


#@app.route('/abc/<x>/<y>')
#def abc(x, y):
#    callanothermethod(x,y)

#You can redirect to the route above like this:

#@app.route('/xyz', methods = ['POST', 'GET'])
#def xyz():
#    if request.method == 'POST':
#       x = request.form["x"]
#       y = request.form["y"]
#       callonemethod(x,y)
#       return redirect(url_for('abc', x=x, y=y))

