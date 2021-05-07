from sqlalchemy import *
from sqlalchemy.orm import relationship
from __main__ import Base
from helpers.hash import *
import time

class User(Base):
	__tablename__ = "Users"

	id = Column(Integer, Sequence('Users_id_seq'), primary_key = True)
	username = Column(String(50))
	passhash = Column(String(750))
	created_utc = Column(Integer)
	creation_ip = Column(String(255))
	is_admin = Column(Boolean, default = False)
	banned_utc = Column(Integer, default = 0)
	ban_expires_utc = Column(Integer, default = 0)
	banned_by_id = Column(Integer, ForeignKey('Users.id'))
	deleted_utc = Column(Integer, default = 0)

	def __init__(self, **kwargs):
		if 'created_utc' not in kwargs:
			kwargs['created_utc'] = int(time.time())

		if 'password' in kwargs:
			kwargs['passhash'] = hash_password(kwargs['password'])
			kwargs.pop('password', None)

		super().__init__(**kwargs)

	def __repr__(self):
		return f"<User(id='{self.id}'; name='{self.username}')>"

	@property
	def is_banned(self):
		return self.banned_utc > 0

	def verify_password(self, password) -> bool:
		return check_password(password, self.passhash)
	