from __main__ import app
from flask import g, session, make_response
from helpers.get import *
from functools import wraps

def auth_desired(f):
	@wraps(f)
	def wrapper(*args, **kwargs):

		u = None

		if 'user_id' in session:
			user = get_user_id(session['user_id'])
			if not user:
				#remove invalid cookie
				session.pop('user_id', None)
			else:
				u = user

		resp = make_response(f(*args, u, **kwargs))
		resp.headers.add("Cache-Control", "private")
		return resp

	return wrapper