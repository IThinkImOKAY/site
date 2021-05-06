from flask import Flask, request, render_template, redirect, g
import yaml
import re
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from os import environ
import time

app = Flask(__name__,static_url_path='')
#with open('main.yaml') as maindb:
#    config = yaml.safe_load(maindb)

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

@app.route('/ping')
def ping():
	return 'pong!'

"""
@app.route('/', methods=['GET'])
def slash():
    boards = config['boards']
    communities = [config['boards'][c]['id'] for c in config['boards']]
    return render_template('index.html',communities=communities)

@app.route('/create_board', methods=['POST','GET'])
def create_board():
    if request.method == 'GET':
        return render_template('create.html',)
    elif request.method == 'POST':
        bid = request.form['id']
        bname = request.form['name']

        if not bid:
            return render_template('create.html', error = "Missing board ID."), 400

            bid = bid.lstrip().rstrip()

        #remove slashes
        if bid.startswith('/'):
            bid = bid[1:]
	
        if bid.endswith('/'):
            bid = bid[:-1]
        
        bid = bid.lower()

        if len(bid) > 4:
            return render_template('create.html', error = "Board ID can't be longer than 4 characters."), 400

        #disallow special characters
        valid_id_regex = re.compile('[a-z]{1,5}')
        if not valid_id_regex.match(bid):
            return render_template('create.html', error = "Board ID cannot contain special characters."), 400

        if config['boards'].get(bid):
            return render_template('create.html', error = "A board with that name already exists."), 409
        else:
            config['boards'][bid] = {'id':bid,'name':bname}
            dump_it(data=config)
            return redirect(f'/{bid}/')
    else:
        return 'invalid method!', 405

@app.route('/<bid>/')
def b(bid):
    if config['boards'].get(bid):
        return render_template('board.html',title=f'/{bid}/',bname=config['boards'][bid]['name'],bid=bid)
    else:
        return 'community does not exist!'

@app.route('/<bid>/submit',methods=['POST'])
def submit(bid):
    title = request.form['title']
    body = request.form['body']
    if config['boards'].get(bid):
        if config['boards'][bid].get('totalposts'):
            pid = config['boards'][bid]['totalposts']+1
            config['boards'][bid]['totalposts']+=1
        else:
            config['boards'][bid]['totalposts']=1
            pid=1
        datadict = {'title':title,'body':body}
        #if config
        config['boards'][bid]['posts'][int(pid)]=datadict
        dump_it(data=config)
        return redirect(f'/{bid}/post/{pid}')
    else:
        return 'board does not exist'

@app.route('/<bid>/post/<pid>',methods=['GET'])
def view_post(bid,pid):
    check = config['boards'][bid]['posts'].get(int(pid))
    if check is not None:
        title = config['boards'][bid]['posts'][int(pid)]['title']
        body = config['boards'][bid]['posts'][int(pid)]['body']
        return render_template('post.html',title=title,body=body)
    else:
        return 'no such post!'
"""

#import routing functions
from routes.boards import *
from routes.posts import *

@app.after_request
def after_request(response):
	g.db.commit()

	return response

if __name__ == '__main__':
	app.run()
