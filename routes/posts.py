from flask import g, render_template, abort, request, redirect
from __main__ import app
from classes.post import *
from helpers.get import *

@app.route('/<boardname>/<int:pid>', methods = ['GET'])
def get_post(boardname, pid):

	b = get_board(boardname, graceful = False)

	post = g.db.query(Post).filter(
		Post.id == pid,
		Post.board_id == b.id).first()

	if not post:
		abort(404)

	return render_template('post.html', post = post)

@app.route('/submit', methods = ['POST'])
def post_submit():
	board = int(request.form.get("board", 1))
	title = request.form.get("title")
	body = request.form.get("body")

	if not title:
		abort(400)

	if not body:
		abort(400)

	title = title.lstrip().rstrip()
	body = body.lstrip().rstrip()

	if len(title) > 50:
		abort(400)

	new_post = Post(title = title,
		body = body,
		board_id = board)

	g.db.add(new_post)
	g.db.flush()

	g.db.refresh(new_post)

	return redirect(new_post.permalink)