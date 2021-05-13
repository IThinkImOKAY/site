from sqlalchemy import *
from sqlalchemy.orm import relationship
from __main__ import Base, cache
import time
from flask import g

class Comment(Base):
    __tablename__ = "Comments"

    id = Column(Integer, Sequence('Comments_id_seq'), primary_key = True)
    body = Column(String(10000))
    created_utc = Column(Integer)
    creation_ip = Column(String(255))
    parent_id = Column(Integer, ForeignKey('Posts.id'))
    is_removed = Column(Boolean, default = False)
    removal_reason = Column(String(255))
    author_id = Column(Integer, ForeignKey('Users.id'))

    parent = relationship(
        "Post",
        lazy = "joined",
        innerjoin = True,
        primaryjoin = "Comment.parent_id == Post.id",
        uselist = False,
        back_populates = "comments"
    )

    author = relationship("User", lazy = "joined", primaryjoin = "Comment.author_id == User.id", uselist = False)

    def __init__(self, **kwargs):
        if 'created_utc' not in kwargs:
            kwargs['created_utc'] = int(time.time())

        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Comment(id='{self.id}')>"

    @property
    @cache.memoize(timeout = 900)
    def permalink(self):
        return f'{self.parent.permalink}#c{self.id}'

    def can_view(self, u) -> bool:
        if not u:
            if self.is_removed or self.parent.is_removed or self.parent.board.is_banned:
                return False

        if u and not u.is_admin:
            if self.parent.board.is_banned:
                return False

            if not self.is_removed and self.parent.is_removed and u.id != self.parent.author_id:
                return False

            if self.is_removed and u.id != self.author_id:
                return False

        return True

    def remove(self, reason = None):
        self.is_removed = True
        self.removal_reason = reason

        g.db.add(self)
