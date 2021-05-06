from flask import g, abort
from classes.board import *

def get_board(boardname, graceful = True) -> Board:
	board = g.db.query(Board).filter_by(name = boardname).first()

	if not board:
		if not graceful:
			abort(404)
		else:
			return None

	return board