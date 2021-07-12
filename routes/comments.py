from flask import g, abort, request, redirect, render_template
from bs4 import BeautifulSoup
import re, os
from werkzeug.utils import secure_filename

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

@app.post('/<boardname>/thread/<int:pid>')
@limiter.limit("10/1minute;30/1hour")
@auth_desired
def post_submit_reply(boardname, pid, u):
    body = request.form.get("body")

    if 'title' in request.form:
        return "Replies cannot have titles.", 400

    parent = get_post(pid, graceful = False)

    if (not u or not u.is_admin) and parent.board.is_banned:
        return render_template("board_banned.html", board = parent.board, u = u), 403

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

    parent.last_bumped_utc = int(g.timestamp)

    if u:
        new_reply.author_id = u.id

    g.db.add(parent)
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

    upload_files = []

    files = request.files.getlist("file")
    for f in files:

        if not f:
            continue

        if not f.content_type.startswith(('image/', 'audio/', 'video')):
            return "file type not allowed", 403

        save_url = os.path.join(app.config["ATTACHMENT_UPLOAD_URL"], f"{new_reply.id}_{secure_filename(f.filename)}")

        f.save(save_url)

        # too large file
        if os.stat(save_url).st_size > app.config.get("MAX_FILE_SIZE")*1000000:
            os.remove(save_url)
            return f"file too large (max <strong>{app.config.get('MAX_FILE_SIZE')}mb</strong> allowed)", 403

        new_file = File(name = f.filename,
            content_type = f.content_type,
            path = save_url,
            upload_ip = request.remote_addr,
            post_id = new_reply.id)

        upload_files.append(new_file)

    g.db.bulk_save_objects(upload_files)

    cache.delete_memoized(new_reply.parent.comment_list)
    cache.delete_memoized(new_reply.board.post_list)

    return redirect(new_reply.permalink)
