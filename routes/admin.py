from __main__ import app, cache, load_config, dump_it
from flask import g, redirect, render_template
from helpers.get import *
from helpers.wrappers import *
from helpers.markdown import *
import threading
import os

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

    if target.is_top_level:
        cache.delete_memoized(target.board.post_list)
    else:
        cache.delete_memoized(target.parent.comment_list)

    files = g.db.query(File).filter(File.post_id.in_(target.idlist)).all()

    for x in files:
        try:
            os.remove(x.path)
        except FileNotFoundError:
            pass
        finally:
            g.db.delete(x)

    for x in target.comments:
        g.db.delete(x)

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

    # remove board from global defaults
    config = dict(load_config())

    if target.url in config.get("default_boards"):
        config["default_boards"] = [x for x in config.get("default_boards") if x != target.url]

        dump_it(config)

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

    posts_query = g.db.query(Post).filter_by(board_id = board.id)

    idlist = [x.id for x in posts_query.all()]

    files = g.db.query(File).filter(File.post_id.in_(idlist)).all()
    for x in files:
        try:
            os.remove(x.path)
        except FileNotFoundError:
            pass
        finally:
            g.db.delete(x)

    posts_query.delete(synchronize_session = False)
    cache.delete_memoized(board.post_list)

    return redirect(board.url)

@app.post('/*/admin/defaults')
@auth_required
@admin_required
@validate_formkey
def admin_toggle_default(u):

    board = get_board(request.form.get("board").strip("/"))

    if not board:
        return render_template("admin/defaults.html", error = "that board doesn't exist", u = u), 404

    config = dict(load_config())

    if board.url in config.get("default_boards"):
        config["default_boards"] = [x for x in config.get("default_boards") if x != board.url]
    else:
        if board.is_banned:
            return render_template("admin/defaults.html", error = f"{board.url} is banned", u = u)

        if len(config.get("default_boards")) >= 15:
            return render_template("admin/defaults.html", error = "max 15 default boards allowed", u = u), 403

        config["default_boards"].append(board.url)

    dump_it(config)

    return render_template("admin/defaults.html", u = u)
