from __main__ import app, cache
from flask import g, redirect
from helpers.get import *
from helpers.wrappers import *

@app.post('/admin/remove/post/<int:pid>')
@auth_required
@admin_required
def admin_remove_post(pid, u):
    target = get_post(pid, graceful = False)

    reason = request.form.get("reason", "")

    target.remove(reason = reason)

    cache.delete_memoized(target.board.post_list)

    return redirect(target.permalink)

@app.post('/admin/remove/comment/<int:cid>')
@auth_required
@admin_required
def admin_remove_comment(cid, u):
    target = get_comment(cid, graceful = False)

    reason = request.form.get("reason", "")

    target.remove(reason = reason)

    cache.delete_memoized(target.parent.comment_list)

    return redirect(target.permalink)

@app.post('/admin/ban/board/<int:bid>')
@auth_required
@admin_required
def admin_ban_board(bid, u):
    target = get_board_id(bid, graceful = False)

    reason = request.form.get("reason", "")

    target.ban(reason = reason)

    return redirect(target.url)

@app.post('/admin/approve/post/<int:pid>')
@auth_required
@admin_required
def admin_approve_post(pid, u):
    target = get_post(pid, graceful = False)

    if not target.is_removed:
        abort(400)

    target.is_removed = False
    target.removal_reason = ""

    g.db.add(target)

    cache.delete_memoized(target.board.post_list)

    return redirect(target.permalink)

@app.post('/admin/approve/comment/<int:cid>')
@auth_required
@admin_required
def admin_approve_comment(cid, u):
    target = get_comment(cid, graceful = False)

    if not target.is_removed:
        abort(400)

    target.is_removed = False
    target.removal_reason = ""

    g.db.add(target)

    cache.delete_memoized(target.parent.comment_list)

    return redirect(target.permalink)

@app.post('/admin/unban/board/<int:bid>')
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
