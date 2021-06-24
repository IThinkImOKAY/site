from flask import Flask, request, render_template, redirect, g, session, abort, jsonify
from flask_caching import Cache
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
from flaskext.markdown import Markdown
import yaml

with open('config.yml', 'r') as _ymlconfig:
    ymlconfig = yaml.safe_load(_ymlconfig)

app = Flask(__name__, static_folder = "./_static")

app.config["RATELIMIT_STORAGE_URL"] = environ.get("REDIS_URL", "memory://")

app.config["CACHE_TYPE"] = "RedisCache"
app.config["CACHE_REDIS_URL"] = environ.get("REDIS_URL")
app.config["CACHE_DEFAULT_TIMEOUT"] = 300

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=['100/minute'],
    strategy="fixed-window"
)


app.config['SECRET_KEY'] = environ.get('MASTER_KEY')

engine = create_engine(environ.get('DB_URL'), echo = True)
Base = declarative_base()

db_session = scoped_session(sessionmaker(bind = engine))

cache = Cache(app)
Markdown(app)

THEMES = [
    'Light',
    'Dark'
]

app.jinja_env.globals['defaultboards'] = ymlconfig.get('default_boards', ['/x/', '/y/', '/z/'])
app.jinja_env.globals['sitename'] = environ.get('SITE_NAME', 'sex')
app.jinja_env.globals['sitecolor'] = environ.get('SITE_COLOR', '#000000')
app.jinja_env.globals['themes'] = THEMES

@app.template_filter('session')
def filter_session(x, default = None):
    return session.get(x, default)

@app.before_request
def before_request():
    g.timestamp = time.time()

    g.db = db_session

    session.permanent = True

    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(16)

from classes.board import *
from helpers.wrappers import *

@app.get('/')
@auth_desired
def index(u):
    boards = g.db.query(Board).all()

    return render_template('home.html', boards = boards, u = u)

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
    except AttributeError:
        pass
    except BaseException:
        g.db.rollback()

        g.db.close()

        abort(500)

    return response

@app.post('/set-theme')
def set_theme():
    response = make_response(redirect(request.referrer))
    #if request.cookies.get('theme'):
    #    response.delete_cookie('theme')
    #else:
    #    response.set_cookie('theme', 'dark')
    theme = request.form.get('theme', 'light')

    if theme not in THEMES:
        abort(400)

    response.set_cookie('theme', theme.lower())

    return response

@app.post('/toggle-favorite')
def toggle_favorite():

    board = request.form.get('board')
    favs = session.get('favorites', [])

    valid_name_regex = re.compile('^/[a-z0-9]{1,5}/$')
    if not valid_name_regex.match(board):
        abort(400)

    if len(favs) > 15:
        abort(409)

    if favs:
        if board in favs:
            session['favorites'] = [x for x in favs if x != board]
        else:
            favs.append(board)
            session['favorites'] = favs
    else:
        session['favorites'] = [request.form.get('board')]

    #print(f"setting favorites to {session['favorites']}")

    return jsonify(session['favorites'])

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
