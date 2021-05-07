from sqlalchemy import *
from sqlalchemy.orm import relationship
from __main__ import Base
from .post import *
import time

class Board(Base):
	__tablename__ = "Boards"

	id = Column(Integer, Sequence('Boards_id_seq'), primary_key = True)
	name = Column(String(4))
	description = Column(String(255))
	created_utc = Column(Integer)
	creation_ip = Column(String(255))

	posts = relationship("Post", primaryjoin = "Board.id == Post.board_id", back_populates = "board")

	def __init__(self, **kwargs):
		if 'created_utc' not in kwargs:
			kwargs['created_utc'] = int(time.time())

		super().__init__(**kwargs)

	def __repr__(self):
		return f"<Board(id='{self.id}'; name='{self.name}')>"

	@property
	def url(self):
		return f'/{self.name}/'
	