from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

base = declarative_base()


class Resource(base):
    __tablename__ = 'resources'

    id = Column(INT, primary_key=True)
    title = Column(VARCHAR)
    author_id = Column(INT)
    course = Column(INT)
    discipline = Column(INT)
    rating = Column(INT)
    file_id = Column(VARCHAR)


class User(base):
    __tablename__ = 'users'

    id = Column(INT, primary_key=True)
    user_id = Column(INT)
    verified = Column(BOOLEAN)
    code = Column(VARCHAR)
    name = Column(VARCHAR)
    email = Column(VARCHAR)


class Mark(base):
    __tablename__ = 'marks'

    id = Column(INT, primary_key=True)
    file_id = Column(VARCHAR)
    user_id = Column(INT)
    mark = Column(SMALLINT)


db = create_engine(os.getenv('DATABASE_URL'))

Session = sessionmaker(db)
session = Session()

base.metadata.create_all(db)
