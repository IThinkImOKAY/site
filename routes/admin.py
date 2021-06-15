from __main__ import app, cache
from flask import g, redirect
from helpers.get import *
from helpers.wrappers import *
from helpers.markdown import *
import threading

def rerender_post(p):
    if p.is_top_level:
        p.body_html = render_md(p.body)
    else:
        p.body_html = render_md(p.body, context = p.parent)

    g.db.add(p)

@app.post('/*/admin/remove/<int:pid>')
@auth_required
@admin_required
@validate_formkey
def admin_remove_post(pid, u):
    target = get_post(pid, graceful = False)

    reason = request.form.get("reason", "")

    _redirect = target.board.url if target.is_top_level else target.parent.permalink

    #rerender_thread = threading.Thread(target = rerender_replies, args = (target,))
    #rerender_thread.run()

    if target.is_top_level:
        cache.delete_memoized(target.board.post_list)

        # delete children
        g.db.query(Post).filter_by(parent_id = target.id).delete(synchronize_session = False)
    else:
        cache.delete_memoized(target.parent.comment_list)

    g.db.delete(target)

    return redirect(_redirect)

@app.post('/*/admin/ban/board/<int:bid>')
@auth_required
@admin_required
@validate_formkey
def admin_ban_board(bid, u):
    target = get_board_id(bid, graceful = False)

    reason = request.form.get("reason", "")

    target.ban(reason = reason)

    return redirect(target.url)

@app.post('/*/admin/approve/<int:pid>')
@auth_required
@admin_required
@validate_formkey
def admin_approve_post(pid, u):
    target = get_post(pid, graceful = False)

    if not target.is_removed:
        abort(400)

    target.is_removed = False
    target.removal_reason = ""

    g.db.add(target)

    rerender_replies(target)

    cache.delete_memoized(target.board.post_list)

    if not target.is_top_level:
        cache.delete_memoized(target.parent.comment_list)

    return redirect(target.permalink)

@app.post('/*/admin/unban/board/<int:bid>')
@auth_required
@admin_required
@validate_formkey
def admin_unban_board(bid, u):
    target = get_board_id(bid, graceful = False)

    if not target.is_banned:
        abort(400)

    target.banned_utc = 0
    target.ban_reason = ""

    g.db.add(target)

    return redirect(target.url)
