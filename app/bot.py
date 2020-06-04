import os
import telebot
import psycopg2
import redis
import utils
import requests
import json
from check_correct import *
from telebot import types

db_conn = psycopg2.connect(os.getenv('DATABASE_URL'), sslmode='require')
redis_conn = redis.Redis.from_url(os.getenv('REDIS_URL'))

TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(
    TOKEN,
#    next_step_backend=utils.RedisHandlerBackend(redis_conn)
)

commands_list = ['/start', '/help', '/search', '/about', '/upload', '/cancel']

def call(message):
    if message.text == '/start':
        handle_start(message)
    elif message.text == '/search':
        handle_search(message)
    elif message.text == '/about':
        handle_about(message)
    elif message.text == '/upload':
        handle_upload(message)
    elif message.text == '/help':
        handle_help(message)


@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    about_start_msg = 'Привет! Этот бот - база данных по специальности с ' \
                'удобным поиском и рейтингом. Мудл на максималках!\n\n' \
                'Вы можете:\n\n' \
                '📤 Загружать различные учебные материалы\n' \
                '🔍 Искать уже загруженные материалы по ключевым словам, темам\n' \
                '📈 Оценивать загруженные материалы, давая другим ' \
                'возможность находить достойные материалы быстрее'
    
    bot.send_message(chat_id, about_start_msg)


@bot.message_handler(commands=['help'])
def handle_help(message):
    chat_id = message.chat.id
    about_help_msg = 'Хэй! Смотри, вот полный список моих команд:\n\n' \
                '📌 /start - прочти ещё разок небольшую справку обо мне!\n' \
                '📌 /search - найди нужный материал в моей библиотеке!\n' \
                '📌 /upload - загрузи свои материалы, чтобы они были доступны другим!\n' \
                '📌 /about - узнай чуть больше о создателях проекта или оставь отзыв/предложение!\n' \
                '📌 /cancel - передумал? останови процесс поиска/загрузки материалов!\n' \
                '📌 /help - посмотри подробную подсказку по командам, если вдруг что-нибудь забудешь:^)'

    bot.send_message(chat_id, about_help_msg)


@bot.message_handler(commands=['search'])
def handle_search(message):
    chat_id = message.chat.id
    about_search_msg = 'Введи поисковый запрос, а я постараюсь тебе помочь!🔍\n\n' \
                'Для выхода из режима поиска введи /cancel'

    instruction = bot.send_message(chat_id, about_search_msg)
    bot.register_next_step_handler(instruction, check_query)


def check_query(message):
    count = 0
    notes = []
    text = message.text.upper()
    chat_id = message.chat.id
    if message.text in commands_list:
        handle_cancel(message, 'поиска')
        call(message)
    elif str(message.text)[0] == '/':
        message_failure = 'Прости, дружок, я тебя не понимаю:(\nИспользуй всплывающие ' \
                'подсказки или /help, если позабыл, какие команды тебе доступны!'

        instruction = bot.send_message(chat_id, message_failure)
        bot.register_next_step_handler(instruction, check_query)
    else:
        cursor = db_conn.cursor()
        cursor.execute("SELECT id, title, course, discipline, file_id FROM resources")
        rows = cursor.fetchall()
        for row in rows:
            if (row[1].upper().find(text) != -1 or str(row[2]).find(text) != -1 or \
                subjects[int(row[3]) - 1].find(text) != -1):
                note = (str(row[0]), row[1], int(row[2]), row[3], row[4])
                notes.append(note)
                count += 1
        if count == 0:
            message_failure = 'Упс, похоже, материалов по твоему запросу ещё нет в ' \
                'моей библиотеке:( Попробуй переформулировать его или первым ' \
                'загрузи материал по теме!'
            bot.send_message(chat_id, message_failure)
        else:
            notes.sort(key = lambda x: x[2])
            for note in notes:
                message_success = 'Материал: ' + note[1] + '\nКурс: ' + str(note[2]) + '\nПредмет: ' + \
                        subjects[int(note[3]) - 1].capitalize() + '\nФайл: '
                file_info = bot.get_file(note[4])
                file = 'https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path)
                markup = types.InlineKeyboardMarkup()
                btn_download = types.InlineKeyboardButton(text = 'Скачать', url = file)
                up_data = json.dumps({'ident': 'up', 'id': note[0]})
                btn_up = types.InlineKeyboardButton(text = "+1", callback_data = up_data)
                down_data = json.dumps({'ident': 'down', 'id': note[0]})
                btn_down = types.InlineKeyboardButton(text = "-1", callback_data = down_data)
                markup.add(btn_down, btn_download, btn_up)
                bot.send_message(chat_id, message_success, reply_markup = markup)
        cursor.close()

    
@bot.callback_query_handler(lambda query: json.loads(query.data)['ident'] == 'up')
def rating_up(query):
    user_id = query.from_user.id
    db_file_id = json.loads(query.data)['id']
    cursor = db_conn.cursor()
    cursor.execute("SELECT file_id FROM resources \
                WHERE id={}".format(db_file_id))
    rows = cursor.fetchall()
    file_id = rows[0][0]
    cursor.close()
    
    cursor = db_conn.cursor()
    cursor.execute("SELECT file_id, user_id, mark FROM marks \
                WHERE file_id='{}' AND user_id={}".format(file_id, str(user_id)))
    rows = cursor.fetchall()
    cursor.close()
    if (len(rows)):
        if (str(rows[0][2]) == '1'):
            cursor = db_conn.cursor()
            cursor.execute("UPDATE marks SET mark=0 \
                WHERE file_id='{}' AND user_id={}".format(file_id, str(user_id)))
            cursor.execute("UPDATE resources SET rating=rating-1 \
                WHERE file_id='{}'".format(file_id))
            cursor.close()
        else:
            cursor = db_conn.cursor()
            cursor.execute("UPDATE marks SET mark=1 \
                WHERE file_id='{}' AND user_id={}".format(file_id, str(user_id)))
            if (str(rows[0][2]) == '0'):
                cursor.execute("UPDATE resources SET rating=rating+1 \
                WHERE file_id='{}'".format(file_id))
            else:
                cursor.execute("UPDATE resources SET rating=rating+2 \
                WHERE file_id='{}'".format(file_id))
            cursor.close()
    else:
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO marks (file_id, user_id, mark) \
                VALUES ('{}', {}, {})".format(file_id, str(user_id), '1'))
        cursor.execute("UPDATE resources SET rating=rating+1 \
            WHERE file_id='{}'".format(file_id))
        cursor.close()
    db_conn.commit()


@bot.callback_query_handler(lambda query: json.loads(query.data)['ident'] == 'down')
def rating_down(query):
    user_id = query.from_user.id
    db_file_id = json.loads(query.data)['id']
    cursor = db_conn.cursor()
    cursor.execute("SELECT file_id FROM resources \
                WHERE id={}".format(db_file_id))
    rows = cursor.fetchall()
    file_id = rows[0][0]
    cursor.close()
    
    cursor = db_conn.cursor()
    cursor.execute("SELECT file_id, user_id, mark FROM marks \
                WHERE file_id='{}' AND user_id={}".format(file_id, str(user_id)))
    rows = cursor.fetchall()
    cursor.close()
    if (len(rows)):
        if (str(rows[0][2]) == '-1'):
            cursor = db_conn.cursor()
            cursor.execute("UPDATE marks SET mark=0 \
                WHERE file_id='{}' AND user_id={}".format(file_id, str(user_id)))
            cursor.execute("UPDATE resources SET rating=rating+1 \
                WHERE file_id='{}'".format(file_id))
            cursor.close()
        else:
            cursor = db_conn.cursor()
            cursor.execute("UPDATE marks SET mark=-1 \
                WHERE file_id='{}' AND user_id={}".format(file_id, str(user_id)))
            if (str(rows[0][2]) == '0'):
                cursor.execute("UPDATE resources SET rating=rating-1 \
                WHERE file_id='{}'".format(file_id))
            else:
                cursor.execute("UPDATE resources SET rating=rating-2 \
                WHERE file_id='{}'".format(file_id))
            cursor.close()
    else:
        cursor = db_conn.cursor()
        cursor.execute("INSERT INTO marks (file_id, user_id, mark) \
                VALUES ('{}', {}, {})".format(file_id, str(user_id), '-1'))
        cursor.execute("UPDATE resources SET rating=rating-1 \
                WHERE file_id='{}'".format(file_id))
        cursor.close()
    db_conn.commit()
    

@bot.message_handler(commands=['upload'])
def handle_upload(message):
    chat_id = message.chat.id
    if check_verification(message.from_user.id):
        options = {'material': None, 'course': None, 'subject': None, 'file': None}
        about_upload_msg = 'Введи название материала для загрузки 📤'
        instruction = bot.send_message(chat_id, about_upload_msg)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_material(user_answer, options))
    else:
        about_upload_msg = 'Загружать материалы могут только зарегистрированные ' \
                'пользователи!\nВведи своё имя и фамилию, пожалуйста!\n\nДля выхода ' \
                'из режима регистрации введи /cancel'
    
        instruction = bot.send_message(chat_id, about_upload_msg)
        bot.register_next_step_handler(instruction, check_name_surname)


def check_verification(user_id):
    cursor = db_conn.cursor()
    cursor.execute("SELECT verified FROM users \
                WHERE user_id={}".format(user_id))
    rows = cursor.fetchall()
    cursor.close()
    return len(rows) and rows[0][0]

def check_material(message, options):
    chat_id = message.chat.id
    if message.text in commands_list:
        handle_cancel(message, 'загрузки')
        call(message)
    elif str(message.text)[0] == '/':
        message_failure = 'Прости, дружок, я тебя не понимаю:(\nИспользуй всплывающие ' \
                'подсказки или /help, если позабыл, какие команды тебе доступны!'

        instruction = bot.send_message(chat_id, message_failure)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_material(user_answer, options))
    elif message.content_type == 'text' and is_material_correct(message):
        options['material'] = message.text
        message_success = 'Теперь укажи курс, к которому относится твой материал'

        instruction = bot.send_message(chat_id, message_success)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_course(user_answer, options))
    else:
        message_failure = 'Упс! Кажется, ты ввёл некорректные данные. ' \
                'попробуй ещё разок, пожалуйста'

        instruction = bot.send_message(chat_id, message_failure)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_material(user_answer, options))


def check_course(message, options):
    chat_id = message.chat.id
    if message.text in commands_list:
        handle_cancel(message, 'загрузки')
        call(message)
    elif str(message.text)[0] == '/':
        message_failure = 'Прости, дружок, я тебя не понимаю:(\nИспользуй всплывающие ' \
                'подсказки или /help, если позабыл, какие команды тебе доступны!'

        instruction = bot.send_message(chat_id, message_failure)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_course(user_answer, options))
    elif message.content_type == 'text' and is_course_correct(message):
        options['course'] = message.text
        message_success = 'И, наконец, введи название предмета, которому соответствует твой материал'

        instruction = bot.send_message(chat_id, message_success)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_subject(user_answer, options))
    else:
        message_failure = 'Упс! Кажется, ты ввёл некорректные данные. ' \
                'попробуй ещё разок, пожалуйста'

        instruction = bot.send_message(chat_id, message_failure)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_course(user_answer, options))


def check_subject(message, options):
    chat_id = message.chat.id
    if message.text in commands_list:
        handle_cancel(message, 'загрузки')
        call(message)
    elif str(message.text)[0] == '/':
        message_failure = 'Прости, дружок, я тебя не понимаю:(\nИспользуй всплывающие ' \
                'подсказки или /help, если позабыл, какие команды тебе доступны!'

        instruction = bot.send_message(chat_id, message_failure)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_subject(user_answer, options))
    elif message.content_type == 'text' and is_subject_correct(message):
        options['subject'] = message.text
        message_success = 'Отлично! Теперь загрузи файл, а я добавлю его в свою библиотеку!'

        instruction = bot.send_message(chat_id, message_success)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_file(user_answer, options))
    else:
        message_failure = 'Упс! Кажется, ты ввёл некорректные данные. ' \
                'попробуй ещё разок, пожалуйста'

        instruction = bot.send_message(chat_id, message_failure)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_subject(user_answer, options))


def check_file(message, options):
    chat_id = message.chat.id
    author_id = message.from_user.id
    if message.text in commands_list:
        handle_cancel(message, 'загрузки')
        call(message)
    elif message.content_type == 'document' and is_file_correct(message):
        file_id = message.document.file_id
        options['file'] = message.document.file_name
        cursor = db_conn.cursor()
        
        cursor.execute("INSERT INTO resources (title, author_id, course, \
        discipline, rating, file_id) VALUES ('{}', {}, \
        {}, '{}', {}, '{}')".format(options['material'], str(author_id), \
        str(options['course']), options['subject'], '0', file_id))

        cursor.close()
        db_conn.commit()
        message_success = 'Отлично! Ваш материал добавлен в базу.'

        bot.send_message(chat_id, message_success)
    else:
        message_failure = 'Упс! Кажется, ты ввёл некорректные данные. ' \
                'попробуй ещё разок, пожалуйста'

        instruction = bot.send_message(chat_id, message_failure)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_file(user_answer, options))


def check_name_surname(message):
    chat_id = message.chat.id
    if message.text in commands_list:
        handle_cancel(message, 'регистрации')
        call(message)
    elif str(message.text)[0] == '/':
        message_failure = 'Прости, дружок, я тебя не понимаю:(\nИспользуй всплывающие ' \
                'подсказки или /help, если позабыл, какие команды тебе доступны!'

        instruction = bot.send_message(chat_id, message_failure)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_name_surname(user_answer, options))
    elif is_name_surname_correct(message):
        message_success = 'Отлично! Теперь укажи адрес своей почты в домене bmstu.ru'

        instruction = bot.send_message(chat_id, message_success)
        bot.register_next_step_handler(instruction, check_email)
    else:
        message_failure = 'Упс! Кажется, ты ввёл некорректные данные. ' \
                'попробуй ещё разок, пожалуйста'

        instruction = bot.send_message(chat_id, message_failure)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_name_surname(user_answer, options))


def check_email(message):
    chat_id = message.chat.id
    if message.text in commands_list:
        handle_cancel(message, 'регистрации')
        call(message)
    elif str(message.text)[0] == '/':
        message_failure = 'Прости, дружок, я тебя не понимаю:(\nИспользуй всплывающие ' \
                'подсказки или /help, если позабыл, какие команды тебе доступны!'

        instruction = bot.send_message(chat_id, message_failure)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_email(user_answer, options))
    elif is_email_correct(message):
        message_success = 'Супер! Чтобы подтвердить регистрацию, напиши ' \
                'мне что-нибудь с этой почты на @bot.bot'
                
        bot.send_message(chat_id, message_success)
    else:
        message_failure = 'Упс! Кажется, ты ввёл некорректные данные. ' \
                'попробуй ещё разок, пожалуйста'

        instruction = bot.send_message(chat_id, message_failure)
        bot.register_next_step_handler(instruction, lambda user_answer: \
            check_email(user_answer, options))


@bot.message_handler(commands=['cancel'])
def handle_cancel(message, mode=None):
    chat_id = message.chat.id
    if mode:
        about_cancel_msg = 'Выход из режима ' + mode

        bot.send_message(chat_id, about_cancel_msg)


@bot.message_handler(commands=['about'])
def handle_about(message):
    chat_id = message.chat.id
    about_author_msg = 'Авторы супер'

    bot.send_message(chat_id, about_author_msg)


@bot.message_handler()
def handle_unknown(message):
    chat_id = message.chat.id
    about_unknown_msg = 'Прости, дружок, я тебя не понимаю:(\nИспользуй всплывающие ' \
                'подсказки или /help, если позабыл, какие команды тебе доступны!'

    bot.send_message(chat_id, about_unknown_msg)