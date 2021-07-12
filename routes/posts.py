from flask import g, render_template, abort, request, redirect
from __main__ import app, limiter, cache
from classes.post import *
from helpers.get import *
from helpers.wrappers import *
import bleach
from werkzeug.utils import secure_filename
import os

from helpers.markdown import *

@app.get('/<boardname>/thread/<int:pid>')
@auth_desired
def get_post(boardname, pid, u):

    b = get_board(boardname, graceful = False)

    post = g.db.query(Post).filter(
        Post.id == pid,
        Post.board_id == b.id).first()

    if not post:
        abort(404)

    if (not u or not u.is_admin) and b.is_banned:
        return render_template("board_banned.html", board = b, u = u), 403

    if post.is_top_level: return render_template('post.html', post = post, u = u)
    else: return redirect(post.permalink)

@app.get('/<boardname>/thread/<int:pid>.source')
@auth_desired
def get_post_markdown(boardname, pid, u):

    b = get_board(boardname, graceful = False)

    post = g.db.query(Post).filter(
        Post.id == pid,
        Post.board_id == b.id).first()

    if not post:
        abort(404)

    if (not u or not u.is_admin) and b.is_banned:
        return render_template("board_banned.html", board = b, u = u), 403

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
        return render_template("board_banned.html", board = board, u = u), 403

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

    upload_files = []

    files = request.files.getlist("file")
    for f in files:

        if not f:
            continue

        if not f.content_type.startswith(('image/', 'audio/', 'video')):
            g.db.delete(new_post)
            return "file type not allowed", 403

        save_url = os.path.join(app.config["ATTACHMENT_UPLOAD_URL"], f"{new_post.id}_{secure_filename(f.filename)}")

        f.save(save_url)

        # too large file
        if os.stat(save_url).st_size > app.config.get("MAX_FILE_SIZE")*1000000:
            os.remove(save_url)
            d.db.delete(new_post)
            return f"file too large (max <strong>{app.config.get('MAX_FILE_SIZE')}mb</strong> allowed)", 403

        new_file = File(name = f.filename,
            content_type = f.content_type,
            path = save_url,
            upload_ip = request.remote_addr,
            post_id = new_post.id)

        upload_files.append(new_file)

    g.db.bulk_save_objects(upload_files)
    cache.delete_memoized(new_post.board.post_list)

    return redirect(new_post.permalink)
