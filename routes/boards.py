from flask import g, render_template, abort, request, redirect
from __main__ import app, limiter
from classes.board import *
import re
from helpers.wrappers import *
from helpers.markdown import *

@app.get('/<boardname>/')
@auth_desired
def get_board(boardname, u):
    board = g.db.query(Board).filter_by(name = boardname).first()

    if not board:
        abort(404)

    if (not u or not u.is_admin) and board.is_banned:
        abort(404)

    return render_template('board.html', board = board, u = u)

@app.get('/board_id/<bid>')
def board_by_id(bid):
    board = g.db.query(Board).filter_by(id = bid).first()

    if not board:
        abort(404)

    return redirect(board.url)

@app.get('/*/create_board')
@auth_required
def get_create_board(u):
    return render_template('create.html', u = u)

@app.post('/*/create_board')
@limiter.limit("10/hour")
@auth_required
@validate_formkey
def post_create_board(u):
    name = request.form.get("name", "")
    title = request.form.get("title", name)
    description = request.form.get("description", "")

    name = name.lstrip().rstrip()

    if not name:
        return render_template('create.html', error = "Missing board name.", u = u), 400

    #remove slashes
    if name.startswith('/'):
        name = name[1:]

    if name.endswith('/'):
        name = name[:-1]

    name = name.lower()

    if len(name) > 5:
        return render_template('create.html', error = "Board name can't be longer than 5 characters.", u = u), 400

    title = title.lstrip().rstrip()

    if len(title) > 25:
        return render_template('create.html', error = "Board title can't be longer than 25 characters.", u = u), 400

    #disallow special characters
    valid_name_regex = re.compile('^[a-z0-9]{1,5}$')
    if not valid_name_regex.match(name):
        return render_template('create.html', error = "Board name cannot contain special characters.", u = u), 400

    #1 board per every 3 days for non-admins
    if not u.is_admin:
        last_board = bool(g.db.query(Board).filter(
            Board.creator_id == u.id,
            Board.created_utc > int(time.time()) - 3*24*60*60
        ).first())

        if last_board:
            return render_template('create.html', error = "You can only create one board every 3 days.", u = u), 429

    #check for already existing board
    existing_board = g.db.query(Board).filter_by(name = name).first()
    if existing_board:
        return render_template('create.html', error = "A board with that name already exists.", u = u), 409

    sidebar_html = render_md(sidebar)

    new_board = Board(name = name,
        title = title,
        description = description,
        sidebar = sidebar,
        sidebar_html = sidebar_html,
        creator_id = u.id,
        creation_ip = request.remote_addr)

    g.db.add(new_board)

    return redirect(new_board.url)
