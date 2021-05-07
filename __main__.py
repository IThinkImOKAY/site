from flask import Flask, request, render_template, redirect, g, session
import re
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from os import environ
import time
import secrets

app = Flask(__name__)

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

    if u:
        return render_template('index.html', boards = boards, u = u)
    else:
        return render_template('index.html', boards = boards)

#import routing functions
from routes.boards import *
from routes.posts import *
from routes.comments import *
from routes.login import *

@app.after_request
def after_request(response):
    g.db.commit()

    g.db.close()

    return response

@app.route('/set-theme', methods=['POST'])
def set_theme():
    response = make_response(redirect(request.referrer))
    if request.cookies.get('theme'):
        response.delete_cookie('theme')
    else:
        response.set_cookie('theme', 'dark')
    return response

if __name__ == '__main__':
	app.run()
