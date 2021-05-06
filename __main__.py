from flask import Flask, request, render_template, redirect, g
import re
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from os import environ
import time

app = Flask(__name__,static_url_path='')

engine = create_engine(environ.get('DB_URL'), echo = True)
Base = declarative_base()

db_session = scoped_session(sessionmaker(bind = engine))

def dump_it(data):
    with open('main.yaml','w') as cf:
        yaml.dump(data,cf)
    return 'dumped!'

@app.before_request
def before_request():
	g.timestamp = time.time()

	g.db = db_session

from classes.board import *

@app.route('/', methods = ['GET'])
def slash():
    boards = g.db.query(Board).all()

    return render_template('index.html', boards = boards)

#import routing functions
from routes.boards import *
from routes.posts import *
from routes.comments import *

@app.after_request
def after_request(response):
    g.db.commit()

    g.db.close()

    return response

if __name__ == '__main__':
	app.run()
