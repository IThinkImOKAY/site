from sqlalchemy import *
from sqlalchemy.orm import relationship
from __main__ import Base
import time
from flask import g

from .comment import *

class Post(Base):
	__tablename__ = "Posts"

	id = Column(Integer, Sequence('Posts_id_seq'), primary_key = True)
	title = Column(String(50))
	body = Column(String(255))
	created_utc = Column(Integer)
	creation_ip = Column(String(255))
	board_id = Column(Integer, ForeignKey('Boards.id'))
	is_removed = Column(Boolean, default = False)
	removal_reason = Column(String(255))
	author_id = Column(Integer, ForeignKey('Users.id'))

	board = relationship("Board", primaryjoin = "Post.board_id == Board.id", innerjoin = True, lazy = "joined", back_populates = "posts")

	comments = relationship("Comment", primaryjoin = "Post.id == Comment.parent_id", back_populates = "parent")

	def __init__(self, **kwargs):
		if 'created_utc' not in kwargs:
			kwargs['created_utc'] = int(time.time())

		super().__init__(**kwargs)

	def __repr__(self):
		return f"<Post(id='{self.id}')>"

	@property
	def permalink(self):
		return f'/{self.board.name}/{self.id}'

	def can_view(self, u) -> bool:
		if (not u or not u.is_admin) and (self.is_removed or self.board.is_banned): return False
		else: return True

	def comment_list(self, u):
		return sorted([c for c in self.comments if c.can_view(u)], key = lambda x: x.created_utc, reverse = True)

	def comment_count(self, u):
		return len(self.comment_list(u))

	def remove(self, reason = None):
		self.is_removed = True
		self.removal_reason = reason

		g.db.add(self)