from __main__ import app
from flask import g, session, redirect, abort, render_template, request
from helpers.get import *
import re
import secrets
from classes.user import *

@app.route('/login', methods = ['GET'])
def get_login():
	if 'user_id' in session:
		return redirect('/')

	return render_template('login.html')

@app.route('/login', methods = ['POST'])
def post_login():
	if 'user_id' in session:
		return redirect('/')

	name = request.form.get('username', '').lstrip().rstrip()
	password = request.form.get('password', '')

	if not name:
		abort(400)

	if not password:
		abort(400)

	user = get_user(name)
	if not user:
		return render_template('login.html', error = "Invalid username."), 404

	if not user.verify_password(password):
		return render_template('login.html', error = "Invalid password."), 401

	if 'session_id' not in session:
		session['session_id'] = secrets.token_hex(16)

	session['user_id'] = user.id

	return redirect('/')

@app.route('/signup', methods = ['GET'])
def get_signup():
	if 'user_id' in session:
		return redirect('/')

	return render_template('signup.html')

@app.route('/signup', methods = ['POST'])
def post_signup():
	if 'user_id' in session:
		return redirect('/')

	name = request.form.get('username', '').lstrip().rstrip()
	password = request.form.get('password', '')	
	password_confirm = request.form.get('password-confirm', '')

	if not name:
		abort(400)

	if not password:
		abort(400)

	if not password_confirm:
		abort(400)

	if password != password_confirm:
		return render_template('signup.html', error = "Passwords must match."), 400

	valid_name_regex = re.compile('[a-zA-Z0-9_]{3,25}')
	if not valid_name_regex.match(name):
		return render_template('signup.html', error = "Usernames must be 3-25 characters long and cannot contain special characters."), 400

	existing_user = get_user(name)
	if existing_user:
		return render_template('signup.html', error = "Username already taken."), 409

	new_user = User(username = name,
		password = password,
		creation_ip = request.remote_addr)

	g.db.add(new_user)
	g.db.flush()

	session['user_id'] = new_user.id

	return redirect('/')