from flask import g, render_template, abort, request, redirect
from __main__ import app
from classes.board import *
import re

@app.route('/<boardname>/')
def get_board(boardname):
	board = g.db.query(Board).filter_by(name = boardname).first()

	if not board:
		abort(404)

	return render_template('board.html', board = board)

@app.route('/create_board', methods = ['GET'])
def get_create_board():
	return render_template('create.html')

@app.route('/create_board', methods = ['POST'])
def post_create_board():
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

	if len(name) > 4:
	    return render_template('create.html', error = "Board name can't be longer than 4 characters."), 400

	#disallow special characters
	valid_id_regex = re.compile('[a-z]{1,5}')
	if not valid_id_regex.match(name):
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