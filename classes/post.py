from sqlalchemy import *
from sqlalchemy.orm import relationship
from __main__ import Base, cache
import time
from flask import g

class Post(Base):
    __tablename__ = "Posts"

    id = Column(Integer, Sequence('Posts_id_seq'), primary_key = True)
    title = Column(String(50))
    body = Column(String(10000))
    body_html = Column(String)
    created_utc = Column(Integer)
    creation_ip = Column(String(255))
    board_id = Column(Integer, ForeignKey('Boards.id'))
    is_removed = Column(Boolean, default = False)
    removal_reason = Column(String(255))
    author_id = Column(Integer, ForeignKey('Users.id'))
    parent_id = Column(Integer, ForeignKey('Posts.id'))
    mentions = Column(ARRAY(Integer), default = [])
    last_bumped_utc = Column(Integer, default = int(time.time()))
    comment_count = Column(Integer, server_default = FetchedValue())

    board = relationship(
        "Board",
        innerjoin = True,
        primaryjoin = "Post.board_id == Board.id",
        uselist = False,
        back_populates = "posts"
    )

    parent = relationship(
        "Post",
        #lazy = "joined",
        primaryjoin = "Post.parent_id == Post.id",
        backref = "comments",
        remote_side = [id]
    )

    author = relationship("User", lazy = "joined", primaryjoin = "Post.author_id == User.id", uselist = False)

    def __init__(self, **kwargs):
        if 'created_utc' not in kwargs:
            kwargs['created_utc'] = int(time.time())

        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Post(id='{self.id}')>"

    @property
    #@cache.memoize(timeout = 900)
    def permalink(self):
        if self.is_top_level: return f'/{self.board.name}/{self.id}'
        else: return f'{self.parent.permalink}#p{self.id}'

    @property
    def created_date(self):
        return time.strftime("%Y/%m/%d (%a) %H:%M:%S UTC", time.gmtime(self.created_utc))

    @property
    def last_bumped_date(self):
        return time.strftime("%y/%m/%d %H:%M:%S UTC", time.gmtime(self.last_bumped_utc))

    @property
    def is_top_level(self):
        return not bool(self.parent_id)

    def can_view(self, u) -> bool:
        if not u:
            if self.is_removed or (self.parent and self.parent.is_removed):
                return False

        if u and not u.is_admin:
            if self.is_removed and u.id != self.author_id:
                return False

        return True

    def can_comment(self, u) -> bool:
        if (not u or not u.is_admin) and (self.is_removed or self.board.is_banned): return False
        else: return True

    @cache.memoize()
    def comment_list(self, u = None):
        return sorted([c for c in self.comments if c.can_view(u)], key = lambda x: x.created_utc, reverse = True)

    #@property
    #def comment_count(self):
    #    return len(self.comments)

    def has_comment(self, cid) -> bool:
        return bool([c for c in self.comments if c.id == cid])

    def remove(self, reason = None):
        self.is_removed = True
        self.removal_reason = reason

        g.db.add(self)
