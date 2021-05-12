from __main__ import app, limiter
from flask import g, session, redirect, abort, render_template, request
from helpers.get import *
import re
import secrets
from classes.user import *

@app.route('/login', methods = ['GET'])
def get_login():
	if 'user_id' in session:
		return redirect('/')

	redirect = request.args.get('redirect', '/')

	return render_template('login.html', redirect = redirect)

@app.route('/login', methods = ['POST'])
def post_login():
	if 'user_id' in session:
		return redirect('/')

	name = request.form.get('username', '').lstrip().rstrip()
	password = request.form.get('password', '')

	redirect_to = request.form.get('redirect', '/')

	if not name:
		abort(400)

	if not password:
		abort(400)

	user = get_user(name)
	if not user:
		return render_template('login.html', error = "Invalid username.", redirect = redirect_to), 404

	if not user.verify_password(password):
		return render_template('login.html', error = "Invalid password.", redirect = redirect_to), 401

	if 'session_id' not in session:
		session['session_id'] = secrets.token_hex(16)

	session['user_id'] = user.id

	return redirect(redirect_to)

@app.route('/signup', methods = ['GET'])
def get_signup():
	if 'user_id' in session:
		return redirect('/')

	redirect = request.args.get('redirect', '/')

	return render_template('signup.html', redirect = redirect)

@app.route('/signup', methods = ['POST'])
@limiter.limit("1/6hours")
def post_signup():
	if 'user_id' in session:
		return redirect('/')

	name = request.form.get('username', '').lstrip().rstrip()
	password = request.form.get('password', '')	
	password_confirm = request.form.get('password-confirm', '')

	redirect_to = request.form.get('redirect', '/')

	if not name:
		abort(400)

	if not password:
		abort(400)

	if not password_confirm:
		abort(400)

	if password != password_confirm:
		return render_template('signup.html', error = "Passwords must match.", redirect = redirect_to), 400

	valid_name_regex = re.compile('^[a-zA-Z0-9_]{3,25}$')
	if not valid_name_regex.match(name):
		return render_template('signup.html', error = "Usernames must be 3-25 characters long and cannot contain special characters.", redirect = redirect_to), 400

	existing_user = get_user(name)
	if existing_user:
		return render_template('signup.html', error = "Username already taken.", redirect = redirect_to), 409

	new_user = User(username = name,
		password = password,
		creation_ip = request.remote_addr)

	g.db.add(new_user)
	g.db.flush()

	session['user_id'] = new_user.id

	return redirect(redirect_to)

@app.route('/logout', methods = ['POST'])
def logout():
	session.pop('user_id', None)

	return redirect(request.referrer)
