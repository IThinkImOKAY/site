from flask import g, render_template, abort, request, redirect
from __main__ import app
from classes.post import *
from helpers.get import *
from helpers.wrappers import *

@app.route('/<boardname>/<int:pid>', methods = ['GET'])
@auth_desired
def get_post(boardname, pid, u):

	b = get_board(boardname, graceful = False)

	post = g.db.query(Post).filter(
		Post.id == pid,
		Post.board_id == b.id).first()

	if not post:
		abort(404)

	if not post.can_view(u):
		abort(404)

	comment_listing = [c for c in post.comments if not c.is_removed] if not u or not u.is_admin else post.comments

	return render_template('post.html', post = post, comment_listing = comment_listing, comment_count = len(comment_listing), u = u)

@app.route('/submit', methods = ['POST'])
@auth_desired
def post_submit(u):
	board_id = int(request.form.get("board", 1))
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

	board = get_board_id(board_id, graceful = False)
	if (not u or not u.is_admin) and board.is_banned:
		abort(404)

	new_post = Post(title = title,
		body = body,
		board_id = board.id,
		creation_ip = request.remote_addr)

	g.db.add(new_post)
	g.db.flush()

	g.db.refresh(new_post)

	return redirect(new_post.permalink)