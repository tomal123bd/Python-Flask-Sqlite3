from __future__ import print_function
import sys, re
from flask import Flask, render_template, request, redirect, url_for
#import mysql.connector
import logging
import smtplib
import requests
import sqlite3
#for sqlite3
#conn.execute('''create table comments (id_data integer primary key  autoincrement,name varchar (255), comment varchar (255),created_by varchar (255))''')
#conn.execute('''create table users (user_id integer primary key autoincrement not null,user_name varchar (255),password varchar (255),email varchar (255))''')

#for mysql
#create table comments (id_data int not null auto_increment,name varchar (255), comment varchar (255),created_by varchar (255), primary key (id_data));
#create table users (user_id int auto_increment not null,user_name varchar (255),password varchar (255),email varchar (255),primary key (user_id));


# from flask_sqlalchemy import SQLAlchemy
# import pymysql
# pymysql.install_as_MySQLdb()
app=Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:111@127.0.0.1:3306/flask_raw_sql'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
# class Comments(db.Model):
# 	id = db.Column(db.Integer, primary_key=True)
# 	name = db.Column(db.String(20))
# 	comment = db.Column(db.String(1000))
conn = sqlite3.connect('cloud_database',check_same_thread=False)
'''
mydb = mysql.connector.connect(
    host="tomal123.mysql.pythonanywhere-services.com",
    user="tomal123",
    passwd="hjbrl311420",
    database="tomal123$cloud_database"
    #database="flask_raw_sql"
    )
'''
login=False
admin_login=False
logged_user=''
mymsg='welcome'
'''***'''
def login_info():
    global login
    app.logger.info(login)
    if login is False:
        return render_template('/front_page.html',msg='Please log in first')
@app.route('/')
def fp():
    return render_template('front_page.html')
@app.route('/create_user',methods=['POST'])
def create_user():
    user_name=request.form['user_name']
    email=request.form['email']
    password=request.form['password']
    #
    mycursor=conn.execute("SELECT * FROM users")
    myresult = mycursor.fetchall()
    if user_name == "":
            return render_template('/front_page.html',msg='Please pick a username')
    if ' ' in user_name:
            return render_template('/front_page.html',msg='Username must not contain any space')
    if '@' and '.' not in email:
        return render_template('/front_page.html',msg='Invalid email address')
    for i in range (len(myresult)):
        if user_name == myresult[i][1]:
            return render_template('/front_page.html',msg='Username Already Exists')
        if email==myresult[i][3]:
            return render_template('/front_page.html',msg='Email Already Exists')

    if len(password)<6:
        return render_template('/front_page.html',msg='Password must be at least 6 characters')
    check_password=bool(re.search(r'(?=.*[a-zA-Z])(?=.*\d)',password))
    if check_password==False:
        return render_template('/front_page.html',msg='Password must contain letters and numbers')
    #
    conn.execute("INSERT INTO users (user_name, password, email) VALUES (?, ?, ?)",(user_name,password,email))
    conn.commit()
    return render_template('/front_page.html',msg='User Created Successfully')

@app.route('/login_user',methods=['POST'])
def login_user():
    user_name=request.form['user_name']
    password=request.form['password']
    mycursor=conn.execute("SELECT * FROM users")
    myresult = mycursor.fetchall()
    for i in range (len(myresult)):
        if user_name == myresult[i][1] and password == myresult[i][2]:
            global login
            global logged_user
            global mymsg
            login=True
            logged_user=myresult[i][1]
            mymsg='Welcome' + ' ' + logged_user
            return redirect (url_for('index'))
    return render_template('/front_page.html',msg='Login failed')

@app.route('/logout_user',methods=['POST'])
def logout_user():
    global login
    global admin_login
    login=False
    admin_login=False
    return render_template('/front_page.html',msg='Logged out')
@app.route('/recover')
def recover():
    return render_template('/recover.html',msg='Enter registered email')
@app.route('/send',methods=['POST'])
def send_mail():
    mycursor=conn.execute("SELECT * FROM users")
    myresult = mycursor.fetchall()
    email=request.form['email']
    for i in range (len(myresult)):
        if email==myresult[i][3]:
            text = 'Your password is: '+myresult[i][2]
            requests.post(
		"https://api.mailgun.net/v3/sandboxcf70286717884a9ba8efb3fce6435b09.mailgun.org/messages",
		auth=("api", "removed for github security reason"),
		data={"from": "Ashikur Rahman <tomal123bd@gmail.com>",
			"to": [email],
			"subject": "Password Request",
			"text": text})
            return render_template('/front_page.html',msg='Password sent,please check inbox or spam folder')
    return render_template('/recover.html',msg='Email not found')
'''***'''
#Admin use only
@app.route('/admin',methods=['POST'])
def admin():
    password=request.form['password']
    if password!='admin':
        return render_template('/front_page.html',msg='Wrong admin passowrd')
    global admin_login
    admin_login=True
    return admin_results()
def admin_results():
    mycursor=conn.execute("SELECT * FROM users")
    user_data = mycursor.fetchall()
    mycursor=conn.execute("SELECT * FROM comments")
    comments_data = mycursor.fetchall()
    mycursor=conn.execute("PRAGMA table_info(users)")
    table_data_users=mycursor.fetchall()
    mycursor=conn.execute("PRAGMA table_info(comments)")
    table_data_comments=mycursor.fetchall()
    return render_template('/admin.html',user_data=user_data,comments_data=comments_data,table_data_users=table_data_users,table_data_comments=table_data_comments)
@app.route('/admin_query',methods=['POST'])
def query():
    #login_info()
    if admin_login is False:
        return render_template('/front_page.html',msg='Please input admin password')
    query=request.form['query']
    conn.execute(query)
    conn.commit()
    return admin_results()
#
@app.route('/profile')
def index():
    #print('test',file=sys.stderr)
    #login_info()
    if login is False:
        return render_template('/front_page.html',msg='Please log in first')
    mycursor=conn.execute("SELECT * FROM comments")
    myresult = mycursor.fetchall()
    mycursor=conn.execute("SELECT * FROM users")
    users=mycursor.fetchall()
    global logged_user
    return render_template('index.html',result=myresult,msg=mymsg,users=users,logged_user=logged_user)
@app.route('/sign')
def sign():
    #login_info()
    if login is False:
        return render_template('/front_page.html',msg='Please log in first')
    return render_template('sign.html')
@app.route('/process',methods=['POST'])
def process():
    #login_info()
    if login is False:
        return render_template('/front_page.html',msg='Please log in first')
    name=request.form['name']
    comment=request.form['comment']
    global logged_user
    conn.execute("INSERT INTO comments (name, comment, created_by) VALUES (?, ?, ?)",(name,comment, logged_user))
    conn.commit()
    global mymsg
    mymsg='successful'
    return redirect(url_for('index'))
@app.route('/delete/<id>',methods=['POST'])
def delete(id):
    #login_info()
    if login is False:
        return render_template('/front_page.html',msg='Please log in first')
    #data=(id,)
    data=(id, )
    conn.execute("delete from comments where id_data = ?",data)
    conn.commit()
    global mymsg
    mymsg='deleted'
    return redirect('/profile')
@app.route('/update/<id>',methods=['POST'])
def update(id):
    #login_info()
    if login is False:
        return render_template('/front_page.html',msg='Please log in first')
    mycursor=conn.execute("SELECT * FROM comments WHERE id_data = ?",id,)
    myresult = mycursor.fetchall()
    return render_template('update.html',data=myresult)
@app.route('/update_data',methods=['POST'])
def update_data():
    #login_info()
    if login is False:
        return render_template('/front_page.html',msg='Please log in first')
    id=request.form['id_data']
    name=request.form['name']
    comment=request.form['comment']
    conn.execute("update comments set name = ? , comment = ? where id_data = ?",(name,comment,id,))
    conn.commit()
    global mymsg
    mymsg='updated'
    return redirect('/profile')
if __name__== '__main__':
    app.run(debug=True)
