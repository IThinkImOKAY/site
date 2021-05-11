from flask import Flask, request, render_template, redirect, g, session, abort
import re
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from os import environ
import time
import secrets
from urllib.parse import quote, urlencode
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=['100/minute'],
)

app.config['SECRET_KEY'] = environ.get('MASTER_KEY')

engine = create_engine(environ.get('DB_URL'), echo = True)
Base = declarative_base()

db_session = scoped_session(sessionmaker(bind = engine))

@app.before_request
def before_request():
    g.timestamp = time.time()

    g.db = db_session

    session.permanent = True

    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(16)

from classes.board import *
from helpers.wrappers import *

@app.route('/', methods = ['GET'])
@auth_desired
def index(u):
    boards = g.db.query(Board).all()

    return render_template('index.html', boards = boards, u = u)

#import routing functions
from routes.boards import *
from routes.posts import *
from routes.comments import *
from routes.login import *
from routes.admin import *

@app.after_request
def after_request(response):
    try:
        g.db.commit()

        g.db.close()
    except BaseException:
        g.db.rollback()

        g.db.close()

        abort(500)

    return response

@app.route('/set-theme', methods=['POST'])
def set_theme():
    response = make_response(redirect(request.referrer))
    if request.cookies.get('theme'):
        response.delete_cookie('theme')
    else:
        response.set_cookie('theme', 'dark')
    return response

@app.errorhandler(401)
def handle_401(e):
    g.db.rollback()
    g.db.close()

    queries = urlencode(dict(request.args))
    path = request.path
    full_path = quote(f"{path}?{queries}", safe = '')

    return redirect(f"/login?redirect={full_path}")

if __name__ == '__main__':
	app.run()
