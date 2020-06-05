from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

base = declarative_base()


class Resource(base):
    __tablename__ = 'resources'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    author_id = Column(Integer)
    course = Column(Integer)
    discipline = Column(Integer)
    rating = Column(Integer)
    file_id = Column(String)


class User(base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    verified = Column(Boolean)
    code = Column(String)
    name = Column(String)
    email = Column(String)


class Mark(base):
    __tablename__ = 'marks'

    id = Column(Integer, primary_key=True)
    file_id = Column(String)
    user_id = Column(Integer)
    mark = Column(SmallInteger)


db = create_engine(os.getenv('DATABASE_URL'))

Session = sessionmaker(db)
session = Session()

base.metadata.create_all(db)
