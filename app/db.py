from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import telebot
import redis
import pickle
import os

base = declarative_base()


class Resource(base):
    __tablename__ = 'resources'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    author_id = Column(Integer)
    course = Column(Integer)
    discipline = Column(String)
    rating = Column(Integer)
    file_id = Column(String)
    views = Column(Integer)
    downloads = Column(Integer)


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


pg_conn = create_engine(os.getenv('DATABASE_URL'))

Session = sessionmaker(pg_conn)
session = Session()

base.metadata.create_all(pg_conn)


class State:
    def __init__(self):
        self.uploading_material = None  # текущий загружаемый материал
        self.registering_user = None  # текущий регистрирующийся пользователь
        self.last_email_date = None  # дата последней отправки письма с кодом
        self.email_attempt = 0  # количество отправленных писем с кодом
        self.code_attempt = 0  # количество неверно введенных кодов


redis_conn = redis.Redis.from_url(os.getenv('REDIS_URL'))


def save_state(user_id, state):
    redis_conn.set(f'state:{user_id}', pickle.dumps(state))


def get_state(user_id):
    key = f'state:{user_id}'

    if not redis_conn.exists(key):
        return {}

    return pickle.loads(redis_conn.get(key))


def clear_state(user_id):
    redis_conn.delete(f'state:{user_id}')


class RedisHandlerBackend(telebot.handler_backends.HandlerBackend):
    def __init__(self, connection, handlers=None):
        super(RedisHandlerBackend, self).__init__(handlers)
        self.prefix = 'telebot'
        self.redis = connection

    def _key(self, handle_group_id):
        return ':'.join((self.prefix, str(handle_group_id)))

    def register_handler(self, handler_group_id, handler):
        handlers = []
        value = self.redis.get(self._key(handler_group_id))
        if value:
            handlers = pickle.loads(value)
        handlers.append(handler)
        self.redis.set(self._key(handler_group_id), pickle.dumps(handlers))

    def clear_handlers(self, handler_group_id):
        self.redis.delete(self._key(handler_group_id))

    def get_handlers(self, handler_group_id):
        handlers = []
        value = self.redis.get(self._key(handler_group_id))
        if value:
            handlers = pickle.loads(value)
            self.clear_handlers(handler_group_id)

        return handlers


next_step_backend = RedisHandlerBackend(redis_conn)
