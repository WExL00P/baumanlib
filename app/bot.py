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
    chat_id = message.chat.id
    about_msg = 'Привет! Этот бот - база данных по специальности с ' \
                'удобным поиском и рейтингом. Мудл на максималках!\n\n' \
                'Вы можете:\n\n' \
                '📤 Загружать различные учебные материалы\n' \
                '🔍 Искать уже загруженные материалы по ключевым словам, темам\n' \
                '📈 Оценивать загруженные материалы, давая другим ' \
                'возможность находить достойные материалы быстрее'
    
    bot.send_message(chat_id, about_msg)


@bot.message_handler(commands=['search'])
def handle_search(message):
    chat_id = message.chat.id
    about_search_msg = 'Введи поисковый запрос\n\n' \
                'Чтобы выйти из режима поиска, введите /cancel'

    bot.send_message(chat_id, about_search_msg)


@bot.message_handler(commands=['upload'])
def handle_upload(message):
    chat_id = message.chat.id
    if check_verification():
        about_upload_msg = 'Введите название материала\n'
        user_answer = bot.send_message(chat_id, about_upload_msg)
        bot.register_next_step_handler(user_answer, check_material)
    else:
        about_upload_msg = 'Для загрузки файлов необходима регистрация.\n\n' \
                'Укажите свое имя и фамилию.\n\n' \
                'Чтобы выйти из режима регистрации, введите /cancel'
    
        user_answer = bot.send_message(chat_id, about_upload_msg)
        bot.register_next_step_handler(user_answer, check_name_surname)


def check_verification():
    return True


def check_material(message):
    chat_id = message.chat.id
    if message.text == '/cancel':
        handle_cancel(message, 'upload')
    else:
        message_success = 'Укажите курс, к которому относится материал'

        user_answer = bot.send_message(chat_id, message_success)
        bot.register_next_step_handler(user_answer, check_course)


def check_course(message):
    chat_id = message.chat.id
    if message.text == '/cancel':
        handle_cancel(message, 'upload')
    else:
        message_success = 'Укажите предмет, к которому относится материал'

        user_answer = bot.send_message(chat_id, message_success)
        bot.register_next_step_handler(user_answer, check_subject)


def check_subject(message):
    chat_id = message.chat.id
    if message.text == '/cancel':
        handle_cancel(message, 'upload')
    else:
        message_success = 'Хорошо, а теперь загрузите файл.'

        user_answer = bot.send_message(chat_id, message_success)
        bot.register_next_step_handler(user_answer, check_file)


def check_file(message):
    chat_id = message.chat.id
    if message.text == '/cancel':
        handle_cancel(message, 'upload')
    elif message.content_type == 'document':
        message_success = 'Отлично! Ваш материал добавлен в базу.\n\n'

        bot.send_message(chat_id, message_success)
    else:
        message_failure = 'Вы отправили что-то не то'

        user_answer = bot.send_message(chat_id, message_failure)
        bot.register_next_step_handler(user_answer, check_file)


def check_name_surname(message):
    chat_id = message.chat.id
    if message.text == '/cancel':
        handle_cancel(message, 'upload')
    else:
        message_success = 'Приятно познакомиться, ' + str(message.text) + '!\n' \
                'Укажите адрес своей почты в домене bmstu.ru\n'

        user_answer = bot.send_message(chat_id, message_success)
        bot.register_next_step_handler(user_answer, check_email)


def check_email(message):
    chat_id = message.chat.id
    if message.text == '/cancel':
        handle_cancel(message, 'upload')
    else:
        message_success = 'Отлично! Классная почта!\n' \
                'Теперь отправьте с этой почты на bot@bot.bot любое сообщение\n'
                
        bot.send_message(chat_id, message_success)


@bot.message_handler(commands=['cancel'])
def handle_cancel(message, mode=None):
    chat_id = message.chat.id
    if mode:
        about_cancel_msg = 'Вы вышли из режима ' + mode

        bot.send_message(chat_id, about_cancel_msg)