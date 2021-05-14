from sqlalchemy import *
from sqlalchemy.orm import relationship
from __main__ import Base
from flask import session
from helpers.hash import *
import time
import secrets

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
    def formkey(self):
        if 'session_id' not in session:
            session['session_id'] = secrets.token_hex(16)

        _formkey = f"{self.id}#{session['session_id']}"

        _formkey = hash(_formkey)
        return _formkey

    def validate_formkey(self, formkey) -> bool:
        return formkey == self.formkey

    @property
    def is_banned(self):
        return self.banned_utc > 0

    def verify_password(self, password) -> bool:
        return check_password(password, self.passhash)
