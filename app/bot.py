import os
import telebot
import psycopg2
import redis
import utils
from check_correct import *

db_conn = psycopg2.connect(os.getenv('DATABASE_URL'), sslmode='require')
redis_conn = redis.Redis.from_url(os.getenv('REDIS_URL'))

bot = telebot.TeleBot(
    os.getenv('TELEGRAM_TOKEN'),
#    next_step_backend=utils.RedisHandlerBackend(redis_conn)
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
    options = {}
    chat_id = message.chat.id
    about_search_msg = 'Введи поисковый запрос\n\n' \
                'Чтобы выйти из режима поиска, введите /cancel'

    instruction = bot.send_message(chat_id, about_search_msg)
    bot.register_next_step_handler(instruction, lambda user_answer: check_query(user_answer, options))


def check_query(message):
    chat_id = message.chat.id
    if message.text == '/cancel':
        handle_cancel(message, 'search')
    else:
        number_of_materials = '10'
        message_success = 'Мне удалось найти ' + number_of_materials + \
                ' материалов.\nВот они:\n\n'

        bot.send_message(chat_id, message_success)


@bot.message_handler(commands=['upload'])
def handle_upload(message):
    chat_id = message.chat.id
    if check_verification():
        options = {'material': None, 'course': None, 'subject': None, 'file': None}
        about_upload_msg = 'Введите название материала\n'
        instruction = bot.send_message(chat_id, about_upload_msg)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_material(user_answer, options))
    else:
        about_upload_msg = 'Для загрузки файлов необходима регистрация.\n\n' \
                'Укажите свое имя и фамилию.\n\n' \
                'Чтобы выйти из режима регистрации, введите /cancel'
    
        instruction = bot.send_message(chat_id, about_upload_msg)
        bot.register_next_step_handler(instruction, check_name_surname)


def check_verification():
    return True


def check_material(message, options):
    chat_id = message.chat.id
    if message.text == '/cancel':
        handle_cancel(message, 'upload')
    elif is_material_correct(message):
        options['material'] = message.text
        message_success = 'Укажите курс, к которому относится материал'

        instruction = bot.send_message(chat_id, message_success)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_course(user_answer, options))
    else:
        message_failure = 'Упс. Попробуй ещё раз!'

        instruction = bot.send_message(chat_id, message_failure)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_material(user_answer, options))


def check_course(message, options):
    chat_id = message.chat.id
    if message.text == '/cancel':
        handle_cancel(message, 'upload')
    elif is_course_correct(message):
        options['course'] = message.text
        message_success = 'Укажите предмет, к которому относится материал'

        instruction = bot.send_message(chat_id, message_success)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_subject(user_answer, options))
    else:
        message_failure = 'Упс. Попробуй ещё раз!'

        instruction = bot.send_message(chat_id, message_failure)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_course(user_answer, options))


def check_subject(message, options):
    chat_id = message.chat.id
    if message.text == '/cancel':
        handle_cancel(message, 'upload')
    elif is_subject_correct(message):
        options['subject'] = message.text
        message_success = 'Хорошо, а теперь загрузите файл.'

        instruction = bot.send_message(chat_id, message_success)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_file(user_answer, options))
    else:
        message_failure = 'Упс. Попробуй ещё раз!'

        instruction = bot.send_message(chat_id, message_failure)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_subject(user_answer, options))


def check_file(message, options):
    chat_id = message.chat.id
    author_id = message.from_user.id
    if message.text == '/cancel':
        handle_cancel(message, 'upload')
    elif message.content_type == 'document' and is_file_correct(message):
        file_id = message.document.file_id
        options['file'] = message.document.file_name
        cursor = db_conn.cursor()
        
        cursor.execute("INSERT INTO resources (title, author_id, course, \
        discipline, rating, type, file_id, link) VALUES ('{0}', {1}, \
        {2}, '{3}', {4}, {5}, '{6}', '{7}')".format(options['material'], str(author_id), \
        str(options['course']), options['subject'], '0', '0', file_id, 'ssilka'))

        cursor.close()
        db_conn.commit()
        message_success = 'Отлично! Ваш материал добавлен в базу.'

        bot.send_message(chat_id, message_success)
    else:
        message_failure = 'Вы отправили что-то не то'

        instruction = bot.send_message(chat_id, message_failure)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_file(user_answer, options))


def check_name_surname(message):
    chat_id = message.chat.id
    if message.text == '/cancel':
        handle_cancel(message, 'upload')
    elif is_name_surname_correct(message):
        message_success = 'Приятно познакомиться, ' + str(message.text) + '!\n' \
                'Укажите адрес своей почты в домене bmstu.ru\n'

        instruction = bot.send_message(chat_id, message_success)
        bot.register_next_step_handler(instruction, check_email)
    else:
        message_failure = 'Упс. Попробуй ещё раз!'

        instruction = bot.send_message(chat_id, message_failure)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_name_surname(user_answer, options))


def check_email(message):
    chat_id = message.chat.id
    if message.text == '/cancel':
        handle_cancel(message, 'upload')
    elif is_email_correct:
        message_success = 'Отлично! Классная почта!\n' \
                'Теперь отправьте с этой почты на bot@bot.bot любое сообщение\n'
                
        bot.send_message(chat_id, message_success)
    else:
        message_failure = 'Упс. Попробуй ещё раз!'

        instruction = bot.send_message(chat_id, message_failure)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_email(user_answer, options))


@bot.message_handler(commands=['cancel'])
def handle_cancel(message, mode=None):
    chat_id = message.chat.id
    if mode:
        about_cancel_msg = 'Вы вышли из режима ' + mode

        bot.send_message(chat_id, about_cancel_msg)