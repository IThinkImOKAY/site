from flask import g, abort, request, redirect
from bs4 import BeautifulSoup
import re

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
@limiter.limit("10/1minute;30/1hour")
@auth_desired
def post_submit_reply(boardname, pid, u):
    body = request.form.get("body")

    if 'title' in request.form:
        return "Replies cannot have titles.", 400

    parent = get_post(pid, graceful = False)

    if not parent.board.name == boardname:
        abort(404)

    body = body.lstrip().rstrip()

    if not body:
        abort(400)

    # ugly hack to make post/board mentions work
    body = body.replace('>>', '\>\>')

    if len(body) > 10000:
        abort(400)

    if not parent.can_comment(u):
        abort(404)

    reply_html = render_md(body, context = parent)

    if len(reply_html) > 10000:
        abort(400)

    new_reply = Post(body = body,
        body_html = reply_html,
        parent_id = parent.id,
        board_id = parent.board.id,
        creation_ip = request.remote_addr)

    if u:
        new_reply.author_id = u.id

    g.db.add(new_reply)
    g.db.flush()

    # get mentions

    soup = BeautifulSoup(reply_html, 'html.parser')
    for m in soup.find_all('a', href = re.compile(r"^#p[0-9]{1,}"), limit = 15):
        mention_id = int(m['href'].lstrip('#p'))

        mention = get_post(mention_id)

        if mention:
            mentions_set = set(mention.mentions)
            mentions_set.add(new_reply.id)

            mention.mentions = list(mentions_set)

            g.db.add(mention)


    g.db.refresh(new_reply)

    cache.delete_memoized(new_reply.parent.comment_list)

    return redirect(new_reply.permalink)
