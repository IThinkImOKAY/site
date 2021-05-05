from flask import Flask, request, render_template, redirect
import yaml
import re

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
            #return 'that board already exists!'
		return render_template('create.html', error = "A board with that name already exists."), 409
        else:
            config['boards'][bid] = {'id':bid,'name':bname}
            dump_it(data=config)
            return redirect('/{}/'.format(bid))
    else:
        return 'invalid method!', 405
        

"""
@app.route('/c/<cid>/')           
def c(cid):
    if config['boards'].get(cid):
        return render_template('board.html',title='/c/'+cid,cname=config['boards'][cid]['name'])
    else:
        return 'community does not exist!'
"""

@app.route('/<bid>/')
def b(bid):
    if config['boards'].get(bid):
        return render_template('board.html',title=f'/{bid}/',cname=config['boards'][bid]['name'])
    else:
        return 'community does not exist!'

if __name__ == '__main__':
	app.run()
