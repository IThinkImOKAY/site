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

@app.post('/*/admin/purge_comments_cache/<pid>')
@auth_required
@admin_required
@validate_formkey
def admin_purge_cached_comments(pid, u):
    target = get_post(pid, graceful = False)

    if not target.is_top_level:
        abort(400)

    cache.delete_memoized(target.comment_list)

    return redirect(target.permalink)

@app.post('/*/admin/move')
@auth_required
@admin_required
@validate_formkey
def admin_move_post(u):
    pid = request.form.get("post")

    if not pid:
        abort(400)

    targets_query = g.db.query(Post).filter(
        or_(
            Post.id == pid,
            Post.parent_id == pid
        )
    )

    op = [x for x in targets_query.all() if x.is_top_level][0]

    # only top level posts can be moved
    if not op:
        abort(400)

    dest = get_board(request.form.get("dest"), graceful = False)

    if dest.id == op.board_id:
        abort(409)

    cache.delete_memoized(op.board.post_list)
    cache.delete_memoized(dest.post_list)

    targets_query.update({Post.board_id: dest.id}, synchronize_session = False)

    g.db.flush()

    g.db.refresh(op)

    return redirect(op.permalink)

@app.post('/*/admin/purge_board')
@auth_required
@admin_required
@validate_formkey
def admin_purge_board(u):

    board = get_board(request.form.get("board", ""), graceful = False)

    g.db.query(Post).filter_by(board_id = board.id).delete(synchronize_session = False)
    cache.delete_memoized(board.post_list)

    return redirect(board.url)
