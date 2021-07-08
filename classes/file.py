from sqlalchemy import *
from sqlalchemy.orm import relationship
from __main__ import Base
#from PIL import Image
#import imagehash
import time

from helpers.hash import hash_file

class File(Base):

    __tablename__ = "files"

    id = Column(Integer, Sequence('files_id_seq'), primary_key = True)
    name = Column(String(100))
    content_type = Column(String(50))
    path = Column(String(255))
    hash = Column(String(255))
    url = Column(String(255))
    upload_ip = Column(String(255))
    upload_utc = Column(Integer)
    post_id = Column(Integer, ForeignKey('Posts.id'))

    post = relationship("Post", primaryjoin = "File.post_id == Post.id", back_populates = "files", uselist = False)

    def __init__(self, **kwargs):

        if 'hash' not in kwargs:
            #_hash = str(imagehash.average_hash(Image.open(kwargs.get("link"))))
            _hash = hash_file(kwargs.get("path"))
            self.hash = _hash

        if 'url' not in kwargs:
            kwargs['url'] = f'/{kwargs["path"]}'

        if 'upload_utc' not in kwargs:
            self.upload_utc = int(time.time())

        super().__init__(**kwargs)
