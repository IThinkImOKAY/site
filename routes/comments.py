from flask import g, abort, request, redirect
from __main__ import app
from classes.comment import *
from helpers.get import *

@app.route('/submit/comment', methods = ['POST'])
def post_submit_comment():
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

	new_comment = Comment(body = body,
		parent_id = parent.id,
		creation_ip = request.remote_addr)

	g.db.add(new_comment)
	g.db.flush()

	g.db.refresh(new_comment)

	return redirect(new_comment.permalink)