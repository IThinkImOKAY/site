from sqlalchemy import *
from sqlalchemy.orm import relationship
from __main__ import Base
import time

class Comment(Base):
	__tablename__ = "Comments"

	id = Column(Integer, Sequence('Comments_id_seq'), primary_key = True)
	body = Column(String(10000))
	created_utc = Column(Integer)
	creation_ip = Column(String(255))
	parent_id = Column(Integer, ForeignKey('Posts.id'))

	parent = relationship(
		"Post",
		primaryjoin = "Comment.parent_id == Post.id",
		innerjoin = True,
		lazy = "joined",
		back_populates = "comments"
	)

	def __init__(self, **kwargs):
		if 'created_utc' not in kwargs:
			kwargs['created_utc'] = int(time.time())

		super().__init__(**kwargs)

	def __repr__(self):
		return f"<Comment(id='{self.id}')>"

	@property
	def permalink(self):
		return f'{self.parent.permalink}#c{self.id}'
	