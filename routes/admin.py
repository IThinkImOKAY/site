from __main__ import app
from flask import g, redirect
from helpers.get import *
from helpers.wrappers import *

@app.route('/admin/remove/post/<int:pid>', methods = ['POST'])
@auth_required
@admin_required
def admin_remove_post(pid, u):
	target = get_post(pid, graceful = False)

	reason = request.form.get("reason", "")

	target.remove(reason = reason)

	return redirect(target.permalink)

@app.route('/admin/remove/comment/<int:cid>', methods = ['POST'])
@auth_required
@admin_required
def admin_remove_comment(cid, u):
	target = get_comment(cid, graceful = False)

	reason = request.form.get("reason", "")

	target.remove(reason = reason)

	return redirect(target.permalink)

@app.route('/admin/ban/board/<int:bid>', methods = ['POST'])
@auth_required
@admin_required
def admin_ban_board(bid, u):
	target = get_board_id(bid, graceful = False)

	reason = request.form.get("reason", "")

	target.ban(reason = reason)

	return redirect(target.url)

@app.route('/admin/approve/post/<int:pid>', methods = ['POST'])
@auth_required
@admin_required
def admin_approve_post(pid, u):
	target = get_post(pid, graceful = False)

	if not target.is_removed:
		abort(400)

	target.is_removed = False
	target.removal_reason = ""

	g.db.add(target)

	return redirect(target.permalink)

@app.route('/admin/approve/comment/<int:cid>', methods = ['POST'])
@auth_required
@admin_required
def admin_approve_comment(cid, u):
	target = get_comment(cid, graceful = False)
	
	if not target.is_removed:
		abort(400)

	target.is_removed = False
	target.removal_reason = ""

	g.db.add(target)

	return redirect(target.permalink)

@app.route('/admin/unban/board/<int:bid>', methods = ['POST'])
@auth_required
@admin_required
def admin_unban_board(bid, u):
	target = get_board_id(bid, graceful = False)
	
	if not target.is_banned:
		abort(400)

	target.banned_utc = 0
	target.ban_reason = ""

	g.db.add(target)

	return redirect(target.url)