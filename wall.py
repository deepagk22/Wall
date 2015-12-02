from flask import Flask, render_template, request, redirect, flash, session, Markup
import re
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'ThisismynewSerectkey'

mysql = MySQLConnector('db')
EMAIL_REGEX = re.compile(r'^[a-za-z0-9\.\+_-]+@[a-za-z0-9\._-]+\.[a-za-z]*$')
@app.route('/')

def index():
	
	return render_template("index.html")


@app.route('/users',methods=['POST'])
def createuser():
	
	error=1
	print "got post info"
	if len(request.form['email']) < 1:
		flash("email: Email cannot be blank!;")
		session["email"]=""
	elif not EMAIL_REGEX.match(request.form['email']):
		flash("email: Invalid Email Address!;")
		session["email"]=""
	else:
		error=0
		session["email"]=request.form['email']

	error=1
	if len(request.form['first_name']) < 1:
		flash("first_name: first name cannot be blank!;")
		session["first_name"]=""

	elif len(request.form['first_name']) < 2:
		flash("first_name: first_name should be more than 2 characters ")
		session["first_name"]=""

	elif bool(re.search(r'\d', request.form['first_name'])):
		flash("first_name: first name cannot have number!;")
		session["first_name"]=""

	else:
		error=0
		session["first_name"]=request.form['first_name']

	error=1
	if len(request.form['last_name']) < 1:
		flash("last_name: last name cannot be blank!;")
		session["last_name"]=""
	elif len(request.form['last_name']) < 2:
		flash("last_name: last_name should be more than 2 characters ")
		session["last_name"]=""
	elif bool(re.search(r'\d', request.form['last_name'])):
		flash("last_name: last name cannot have number!;")
		session["last_name"]=""
	else:
		error=0
		session["last_name"]=request.form['last_name']
	error=1
	session["password"]=""
	session["confirm_password"]=""
	if len(request.form['password']) < 1:
		flash("password: password cannot be blank!;")
	elif len(request.form['password']) < 8:
		flash("password: Password should be more than 8 characters ")
	elif len(request.form['confirm_password']) < 1 or request.form['password'] != request.form['confirm_password']:
		flash("confirm_password: Password and Confirm Password do not match;")
	else:
		error=0
		session["password"]=request.form['password']
		session["confirm_password"]=request.form['confirm_password']
	
	if error==0:
		return redirect("/register")
	else:
		return redirect("/")

@app.route('/register')
def registeruser():
	pw_hash = bcrypt.generate_password_hash(session["password"])
	sqlstmt="insert into users(email,first_name,last_name,password) values('"+session["email"]+"','"+session["first_name"]+"', '"+session["last_name"]+"', '"+pw_hash+"')"
	session["password"]=""
	session["confirm_password"]=""
	session["message"]=""
	print sqlstmt 
	mysql.run_mysql_query(sqlstmt)
	fetchValue(0)
	return redirect("/show")

def fetchValue(userid):
	sqlstmt="select * from messages inner join users where users.id=messages.users_id  ORDER BY message_created_by DESC"
	print sqlstmt
	allemail= mysql.fetch(sqlstmt)
	print allemail
	
	for i in range(0,len(allemail)):
		session["message"]+="<div><div><b>"+allemail[i]["first_name"]+"&nbsp;"+allemail[i]["last_name"]+" </b>"+str(allemail[i]["message_created_by"])+"</div>"
		session["message"]+= "<div>"+allemail[i]["message"]+"</div></div>"

@app.route('/login', methods=["POST"])
def login():
	session["message"]=""
	sqlstmt="select * from users where email='"+request.form["loginuser"]+"'"

	print sqlstmt 
	allemail= mysql.fetch(sqlstmt)
	if len(allemail)>0:
		if(bcrypt.check_password_hash(allemail[0]["password"], request.form["loginpassword"])):
			print "success"
			# session["first_name"]=allemail[0]["first_name"]
			# session["last_name"]=allemail[0]["last_name"]
			session["userid"]=allemail[0]["id"]
			session["message"]=""
			fetchValue(allemail[0]["id"])


			return redirect("/show")
	flash("Invalid Username and password")
	return redirect("/")

@app.route('/show')
def show():
	sessionmessage=Markup(session["message"])
	return render_template("wall.html",sessionmessage=sessionmessage)

@app.route('/postmsgcall', methods=["POST"])
def postMsg():
	sqlstmt="insert into messages(message,users_id) values('"+str(request.form["msg"])+"',"+str(session["userid"])+")"
	print sqlstmt 
	mysql.run_mysql_query(sqlstmt)
	fetchValue(session["userid"])

	return redirect("/show")
@app.route('/logout')
def logout():
	session.clear()
	return redirect ("/")
app.run(debug=True)
