import os
import pickle
import smtplib
import re
import telebot
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(address, subject, body):
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login(os.getenv('EMAIL_ADDRESS'), os.getenv('EMAIL_PASSWORD'))

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        server.sendmail(os.getenv('EMAIL_ADDRESS'), address, msg.as_string())
        server.quit()
    except:
        print("Email failed to send.")


def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"
                               u"\U0001F300-\U0001F5FF"
                               u"\U0001F680-\U0001F6FF"
                               u"\U0001F1E0-\U0001F1FF"
                               "]+", flags=re.UNICODE)

    return emoji_pattern.sub(r'', string)


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
