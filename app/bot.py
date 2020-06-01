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
    about_msg = 'Привет! Этот бот - база данных по специальности с ' \
                'удобным поиском и рейтингом. Мудл на максималках!\n\n' \
                'Вы можете:\n\n' \
                '📤 Загружать различные учебные материалы\n' \
                '🔍 Искать уже загруженные материалы по ключевым словам, темам\n' \
                '📈 Оценивать загруженные материалы, давая другим ' \
                'возможность находить достойные материалы быстрее'
    
    bot.send_message(message.chat.id, about_msg)


@bot.message_handler(commands=['search'])
def handle_search(message):
    about_search_msg = 'Введи поисковый запрос\n\n' \
                'Чтобы выйти из режима поиска, введите /cancel'

    bot.send_message(message.chat.id, about_search_msg)


@bot.message_handler(commands=['upload'])
def handle_upload(message):
    about_upload_msg = 'Для загрузки файлов необходима регистрация.\n\n' \
                'Укажите свое имя и фамилию.\n\n' \
                'Чтобы выйти из режима регистрации, введите /cancel'
    
    user_answer = bot.send_message(message.chat.id, about_upload_msg)
    bot.register_next_step_handler(user_answer, check_name_surname)


def check_name_surname(message):
    if message.text == '/cancel':
        handle_cancel(message, 'upload')
    else:
        message_success = 'Приятно познакомиться, ' + str(message.text) + '!\n' \
                'Укажите адрес своей почты в домене bmstu.ru\n'

        user_answer = bot.send_message(message.chat.id, message_success)
        bot.register_next_step_handler(user_answer, check_email)


def check_email(message):
    if message.text == '/cancel':
        handle_cancel(message, 'upload')
    else:
        message_success = 'Отлично! Классная почта!\n' \
                'Теперь отправьте с этой почты на bot@bot.bot любое сообщение\n'
                
        bot.send_message(message.chat.id, message_success)


@bot.message_handler(commands=['cancel'])
def handle_cancel(message, mode=None):
    if mode:
        about_cancel_msg = 'Вы вышли из режима ' + mode

        bot.send_message(message.chat.id, about_cancel_msg)