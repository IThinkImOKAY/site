from flask import Flask, request, render_template, redirect
import yaml

app = Flask(__name__,static_url_path='')
with open('main.yaml') as maindb:
    config = yaml.safe_load(maindb)

def dump_it(data):
    with open('main.yaml','w') as cf:
        yaml.dump(data,cf)
    return 'dumped!'

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
        if config['boards'].get(bid):
            return 'that board already exists!'
        else:
            config['boards'][bid] = {'id':bid,'name':bname}
            dump_it(data=config)
            return redirect('/c/{}'.format(bid))
    else:
        return 'invalid method!'
        

@app.route('/c/<cid>/')           
def c(cid):
    if config['boards'].get(cid):
        return render_template('board.html',title='/c/'+cid,cname=config['boards'][cid]['name'])
    else:
        return 'community does not exist!'
