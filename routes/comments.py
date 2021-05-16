from flask import g, abort, request, redirect
from __main__ import app, limiter, cache
from classes.post import *
from helpers.get import *
from helpers.wrappers import *
from helpers.markdown import *

@app.get('/post_id/<int:pid>')
@auth_desired
def post_by_id(pid, u):
    post = get_post(pid, graceful = False)

    if not post.can_view(u):
        abort(404)

    return redirect(post.permalink)

@app.post('/<boardname>/<int:pid>')
@limiter.limit("1/10seconds;5/1minute;30/1hour")
@auth_desired
def post_submit_reply(boardname, pid, u):
    body = request.form.get("body")

    if 'title' in request.form:
        return "Replies cannot have titles.", 400

    parent = get_post(pid, graceful = False)

    if not parent.board.name == boardname:
        abort(404)

    if not body:
        abort(400)

    body = body.lstrip().rstrip()

    if len(body) > 10000:
        abort(400)

    if not parent.can_comment(u):
        abort(404)

    reply_html = render_md(body, context = parent)

    new_reply = Post(body = body,
        body_html = reply_html,
        parent_id = parent.id,
        board_id = parent.board.id,
        creation_ip = request.remote_addr)

    if u:
        new_reply.author_id = u.id

    g.db.add(new_reply)
    g.db.flush()

    g.db.refresh(new_reply)

    cache.delete_memoized(new_reply.parent.comment_list)

    return redirect(new_reply.permalink)
