from sqlalchemy import *
from sqlalchemy.orm import relationship
from __main__ import Base, cache
from .post import *
import time
from flask import g

class Board(Base):
    __tablename__ = "Boards"

    id = Column(Integer, Sequence('Boards_id_seq'), primary_key = True)
    name = Column(String(5))
    description = Column(String(255))
    created_utc = Column(Integer)
    creation_ip = Column(String(255))
    banned_utc = Column(Integer, default = 0)
    ban_reason = Column(String(255))
    creator_id = Column(Integer, ForeignKey('Users.id'))

    posts = relationship("Post", primaryjoin = "Board.id == Post.board_id", back_populates = "board")

    creator = relationship("User", primaryjoin = "Board.creator_id == User.id", uselist = False)

    def __init__(self, **kwargs):
        if 'created_utc' not in kwargs:
            kwargs['created_utc'] = int(time.time())

        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Board(id='{self.id}'; name='{self.name}')>"

    @property
    def is_banned(self):
        return self.banned_utc > 0

    @property
    def url(self):
        return f'/{self.name}/'

    @cache.memoize(timeout = 900)
    def post_list(self, u = None):
        return sorted([p for p in self.posts if p.can_view(u)], key = lambda x: x.created_utc, reverse = True)

    def ban(self, reason = None):
        self.banned_utc = int(time.time())
        self.ban_reason = reason

        g.db.add(self)
