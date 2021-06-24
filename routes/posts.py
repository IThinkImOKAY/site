from flask import g, render_template, abort, request, redirect
from __main__ import app, limiter, cache
from classes.post import *
from helpers.get import *
from helpers.wrappers import *
import bleach

from helpers.markdown import *

@app.get('/<boardname>/<int:pid>')
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

    b.__dict__["_favorite"] = b.url in session.get("favorites", [])

    if post.is_top_level: return render_template('post.html', post = post, u = u)
    else: return redirect(post.permalink)

@app.get('/<boardname>/<int:pid>.source')
@auth_desired
def get_post_markdown(boardname, pid, u):

    b = get_board(boardname, graceful = False)

    post = g.db.query(Post).filter(
        Post.id == pid,
        Post.board_id == b.id).first()

    if not post:
        abort(404)

    if not post.can_view(u):
        abort(404)

    return bleach.clean(post.body, tags = [])

@app.post('/<boardname>/')
@limiter.limit("1/3minutes")
@auth_desired
def post_submit(boardname, u):
    board_id = int(request.form.get("board", 1))
    title = request.form.get("title")
    body = request.form.get("body")

    title = title.lstrip().rstrip()

    if not body:
        abort(400)

    body = body.lstrip().rstrip()

    if len(title) > 50:
        abort(400)

    board = get_board(boardname, graceful = False)
    if (not u or not u.is_admin) and board.is_banned:
        abort(404)

    post_html = render_md(body)

    new_post = Post(title = title,
        body = body,
        body_html = post_html,
        board_id = board.id,
        creation_ip = request.remote_addr)

    if u:
        new_post.author_id = u.id

    g.db.add(new_post)
    g.db.flush()

    g.db.refresh(new_post)

    cache.delete_memoized(new_post.board.post_list)

    return redirect(new_post.permalink)
