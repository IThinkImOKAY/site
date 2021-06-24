from flask import g, abort
from classes.board import *
from classes.post import *
from classes.user import *

def get_board(boardname, graceful = True) -> Board:
    board = g.db.query(Board).filter_by(name = boardname).first()

    if not board:
        if not graceful:
            abort(404)
        else:
            return None

    return board

def get_board_id(bid, graceful = True) -> Board:
    board = g.db.query(Board).filter_by(id = bid).first()

    if not board:
        if not graceful:
            abort(404)
        else:
            return None

    return board

def get_post(pid, graceful = True) -> Post:
    post = g.db.query(Post).filter_by(id = pid).first()

    if not post:
        if not graceful:
            abort(404)
        else:
            return None

    return post

def get_user(username, graceful = True) -> User:
    user = g.db.query(User).filter_by(username = username).first()

    if not user:
        if not graceful:
            abort(404)
        else:
            return None

    return user

def get_user_id(uid, graceful = True) -> User:
    user = g.db.query(User).filter_by(id = uid).first()

    if not user:
        if not graceful:
            abort(404)
        else:
            return None

    return user
