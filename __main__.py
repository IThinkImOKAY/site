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
        datadict = {'title':title,'body':body,'comments':{},'num_comments':0}
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
        comments = config['boards'][bid]['posts'][int(pid)]['comments']
        return render_template('post.html',title=title,body=body,pid=pid,bid=bid,comments=comments)
    else:
        return 'no such post!'

@app.route('/<bid>/post/<pid>/comment/',methods=['POST'])
def comment(bid,pid):
    body = request.form.get('body')
    if body is not None:
        num_comments = config['boards'][bid]['posts'][int(pid)]['num_comments']
        com_count = int(num_comments)+1
        config['boards'][bid]['posts'][int(pid)]['num_comments']+=1
        commentdict = {'body':body}#,'number':num_count}
        config['boards'][bid]['posts'][int(pid)]['comments'][com_count] = commentdict
        dump_it(data=config)
        return redirect(request.path.replace('/comment/',''))
    else:
        return 'no body provided!'

if __name__ == '__main__':
	app.run()
