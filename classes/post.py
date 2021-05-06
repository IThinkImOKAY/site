from sqlalchemy import *
from sqlalchemy.orm import relationship
from __main__ import Base
import time

from .comment import *

class Post(Base):
	__tablename__ = "Posts"

	id = Column(Integer, Sequence('Posts_id_seq'), primary_key = True)
	title = Column(String(50))
	body = Column(String(255))
	created_utc = Column(Integer)
	creation_ip = Column(String(255))
	board_id = Column(Integer, ForeignKey('Boards.id'))

	board = relationship("Board", primaryjoin = "Post.board_id == Board.id", innerjoin = True, lazy = "joined", back_populates = "posts")

	comments = relationship("Comment", primaryjoin = "Post.id == Comment.parent_id", back_populates = "parent")

	def __init__(self, **kwargs):
		if 'created_utc' not in kwargs:
			kwargs['created_utc'] = int(time.time())

		super().__init__(**kwargs)

	@property
	def permalink(self):
		return f'/{self.board.name}/{self.id}'