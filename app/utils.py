import pickle
import telebot

class RedisHandlerBackend(telebot.handler_backends.HandlerBackend):
    def __init__(self, connection, handlers=None, prefix='telebot'):
        super(RedisHandlerBackend, self).__init__(handlers)
        self.prefix = prefix
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
