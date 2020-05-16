import os
import telebot
import psycopg2
import redis
import utils

db_conn = psycopg2.connect(os.getenv('DATABASE_URL'), sslmode='require')
redis_conn = redis.Redis.from_url(os.getenv('REDIS_URL'))

bot = telebot.TeleBot(
    os.getenv('TELEGRAM_TOKEN'),
    next_step_backend=utils.RedisHandlerBackend(redis_conn)
)

@bot.message_handler()
def echo(message):
    bot.reply_to(message, message.text)

@bot.message_handler(content_types=['document'])
def echo_doc(message):
    bot.send_document(message.chat.id, message.document.file_id)
