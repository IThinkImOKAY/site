from flask import g, abort, request, redirect
from __main__ import app, limiter
from classes.comment import *
from helpers.get import *
from helpers.wrappers import *

@app.route('/comment/<int:cid>', methods = ['GET'])
@auth_desired
def comment_by_id(cid, u):
	comment = get_comment(cid, graceful = False)

	if not comment.can_view(u):
		abort(404)

	return redirect(comment.permalink)

@app.route('/submit/comment', methods = ['POST'])
@limiter.limit("1/minute")
@auth_desired
def post_submit_comment(u):
	parent_id = int(request.form.get("parent"))
	body = request.form.get("body")

	if not parent_id:
		abort(400)

	if not body:
		abort(400)

	body = body.lstrip().rstrip()

	if len(body) > 10000:
		abort(400)

	parent = get_post(parent_id, graceful = False)

	if not parent.can_comment(u):
		abort(404)

	new_comment = Comment(body = body,
		parent_id = parent.id,
		creation_ip = request.remote_addr)

	if u:
		new_comment.author_id = u.id

	g.db.add(new_comment)
	g.db.flush()

	g.db.refresh(new_comment)

	return redirect(new_comment.permalink)
