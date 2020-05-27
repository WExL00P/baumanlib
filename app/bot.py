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


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    about_msg = 'Привет! Этот бот - база данных по специальности с' \
                'удобным поиском и рейтингом. Мудл на максималках!\n\n' \
                'Вы можете:\n\n' \
                '📤 Загружать различные учебные материалы\n' \
                '🔍 Искать уже загруженные материалы по ключевым словам, темам\n' \
                '📈 Оценивать загруженные материалы, давая другим возможность' \
                'находить достойные материалы быстрее'
    
    bot.send_message(message.chat.id, about_msg)
