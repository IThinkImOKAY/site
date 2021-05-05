from flask import Flask, request, render_template, redirect
import yaml

app = Flask(__name__,static_url_path='')
with open('main.yaml') as maindb:
    config = yaml.safe_load(maindb)

@app.route('/', methods=['GET'])
def slash():
    boards = config['boards']
    communities = [config['boards'][c]['id'] for c in config['boards']]
    return render_template('index.html',communities=communities)

#@app.route('/create_board', methods=['GET'])
#def get_create_board():
#    return render_template('create.html',)

@app.route('/c/<cid>/')
def c(cid):
    return cid
