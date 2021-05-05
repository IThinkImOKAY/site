from sqlalchemy import *
from __main__ import Base
import time

class Board(Base):
	__tablename__ = "Boards"

	id = Column(Integer, Sequence('Boards_id_seq'), primary_key = True)
	name = Column(String(4))
	description = Column(String(255))
	created_utc = Column(Integer)
	creation_ip = Column(String(255))

	def __init__(self, **kwargs):
		if 'created_utc' not in kwargs:
			kwargs['created_utc'] = int(time.time())

		super().__init__(**kwargs)