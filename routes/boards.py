from flask import g, render_template, abort, request, redirect
from __main__ import app, limiter
from classes.board import *
import re
from helpers.wrappers import *

@app.get('/<boardname>/')
@auth_desired
def get_board(boardname, u):
	board = g.db.query(Board).filter_by(name = boardname).first()

	if not board:
		abort(404)

	if (not u or not u.is_admin) and board.is_banned:
		abort(404)

	return render_template('board.html', board = board, u = u)

@app.get('/board_id/<bid>')
def board_by_id(bid):
	board = g.db.query(Board).filter_by(id = bid).first()

	if not board:
		abort(404)

	return redirect(board.url)

@app.get('/create_board')
@auth_required
def get_create_board(u):
	return render_template('create.html', u = u)

@app.post('/create_board')
@limiter.limit("1/3days")
@auth_required
def post_create_board(u):
	name = request.form['name']
	desc = request.form['desc']

	if not name:
	    return render_template('create.html', error = "Missing board name."), 400

	name = name.lstrip().rstrip()

	#remove slashes
	if name.startswith('/'):
	    name = name[1:]

	if name.endswith('/'):
	    name = name[:-1]

	name = name.lower()

	if len(name) > 5:
	    return render_template('create.html', error = "Board name can't be longer than 5 characters."), 400

	#disallow special characters
	valid_name_regex = re.compile('^[a-z]{1,5}$')
	if not valid_name_regex.match(name):
	    return render_template('create.html', error = "Board name cannot contain special characters."), 400

	#check for already existing board
	existing_board = g.db.query(Board).filter_by(name = name).first()
	if existing_board:
		return render_template('create.html', error = "A board with that name already exists."), 409

	new_board = Board(name = name,
		description = desc,
		creation_ip = request.remote_addr)

	g.db.add(new_board)

	return redirect(new_board.url)
