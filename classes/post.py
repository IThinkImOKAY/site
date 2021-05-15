from sqlalchemy import *
from sqlalchemy.orm import relationship
from __main__ import Base, cache
import time
from flask import g

from .comment import *

from helpers.markdown import *

class Post(Base):
    __tablename__ = "Posts"

    id = Column(Integer, Sequence('Posts_id_seq'), primary_key = True)
    title = Column(String(50))
    body = Column(String(255))
    body_html = Column(String(10000))
    created_utc = Column(Integer)
    creation_ip = Column(String(255))
    board_id = Column(Integer, ForeignKey('Boards.id'))
    is_removed = Column(Boolean, default = False)
    removal_reason = Column(String(255))
    author_id = Column(Integer, ForeignKey('Users.id'))

    board = relationship(
        "Board",
        lazy = "joined",
        innerjoin = True,
        primaryjoin = "Post.board_id == Board.id",
        uselist = False,
        back_populates = "posts"
    )

    comments = relationship("Comment", primaryjoin = "Post.id == Comment.parent_id", back_populates = "parent")

    author = relationship("User", lazy = "joined", primaryjoin = "Post.author_id == User.id", uselist = False)

    def __init__(self, **kwargs):
        if 'created_utc' not in kwargs:
            kwargs['created_utc'] = int(time.time())

        kwargs['body_html'] = render(kwargs['body'])

        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Post(id='{self.id}')>"

    @property
    @cache.memoize(timeout = 900)
    def permalink(self):
        return f'/{self.board.name}/{self.id}'

    def can_view(self, u) -> bool:
        if not u:
            if self.is_removed or self.board.is_banned:
                return False

        if u and not u.is_admin:
            if self.board.is_banned:
                return False

            if self.is_removed and u.id != self.author_id:
                return False

        return True

    def can_comment(self, u) -> bool:
        if (not u or not u.is_admin) and (self.is_removed or self.board.is_banned): return False
        else: return True

    @cache.memoize(timeout = 900)
    def comment_list(self, u = None):
        return sorted([c for c in self.comments if c.can_view(u)], key = lambda x: x.created_utc, reverse = True)

    def comment_count(self, u):
        return len(self.comment_list(u))

    def remove(self, reason = None):
        self.is_removed = True
        self.removal_reason = reason

        g.db.add(self)
