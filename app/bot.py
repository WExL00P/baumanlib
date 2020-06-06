import os
import telebot
import redis
import json
from check_correct import *
from telebot.types import (
    KeyboardButton, ReplyKeyboardMarkup,
    ReplyKeyboardRemove, InlineKeyboardButton,
    InlineKeyboardMarkup
)
from message_templates import *
from db import session, Resource, Mark, User
from utils import (
    send_email, remove_emoji,
    ALL_CONTENT_TYPES, RedisHandlerBackend
)
from xml.sax.saxutils import escape
from config import SUBJECTS, COMMANDS

redis_conn = redis.Redis.from_url(os.getenv('REDIS_URL'))

TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(
    TOKEN,
    next_step_backend=RedisHandlerBackend(redis_conn)
)


uploading_material = None
registering_user = None


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
    bot.send_message(chat_id, START_MSG)


@bot.message_handler(commands=['help'])
def handle_help(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, HELP_MSG)


@bot.message_handler(commands=['search'])
def handle_search(message):
    chat_id = message.chat.id
    instruction = bot.send_message(chat_id, SEARCH_MSG)
    bot.register_next_step_handler(instruction, check_query)


def generate_result_markup(material_id):
    markup = InlineKeyboardMarkup()

    dwn_data = json.dumps({'action': 'download', 'id': material_id})
    btn_download = InlineKeyboardButton(text='Скачать', callback_data=dwn_data)

    up_data = json.dumps({'action': 'up', 'id': material_id, 'value': 1})
    btn_up = InlineKeyboardButton(text='+1', callback_data=up_data)

    down_data = json.dumps({'action': 'down', 'id': material_id, 'value': -1})
    btn_down = InlineKeyboardButton(text='-1', callback_data=down_data)

    markup.add(btn_down, btn_download, btn_up)
    return markup


def check_query(message):
    chat_id = message.chat.id

    if message.text in COMMANDS:
        return handle_cancel(message, 'поиска')

    if message.content_type != 'text' or message.text.startswith('/'):
        instruction = bot.send_message(chat_id, INCORRECT_DATA_MSG)
        return bot.register_next_step_handler(instruction, check_query)

    query = f'%{message.text}%'
    resources = session.query(Resource) \
        .filter(Resource.title.ilike(query)) \
        .order_by(Resource.rating.asc())

    resources_n = resources.count()

    if resources_n == 0:
        return bot.send_message(chat_id, NO_RESULTS_MSG)

    for r in resources:
        result = f'<b>{r.title}</b>\n\n' \
                 f'{SUBJECTS[r.discipline]}\n' \
                 f'🎓 {r.course} курс\n' \
                 f'📊 Рейтинг: {r.rating}'

        markup = generate_result_markup(r.id)
        bot.send_message(chat_id, result, reply_markup=markup, parse_mode='html')

    bot.send_message(chat_id, search_found_msg(resources_n))


@bot.callback_query_handler(
    lambda query: json.loads(query.data)['action'] in ['up', 'down'])
def change_rating(query):
    query_json = json.loads(query.data)

    user_id = query.from_user.id
    file_id = query_json['id']
    rating = query_json['value']

    resource = session.query(Resource) \
        .filter(Resource.id == file_id)

    if resource.count() == 0:
        return

    resource = resource.one()

    mark_row = session.query(Mark) \
        .filter(Mark.file_id == resource.file_id) \
        .filter(Mark.user_id == user_id)

    if mark_row.count() != 0:
        mark_row = mark_row.one()

        if mark_row.mark == rating:
            mark_row.mark = 0
            resource.rating -= rating
            msg = 'Голос отозван'
        else:
            if mark_row.mark == 0:
                resource.rating += rating
                msg = f'Материал оценён на {rating}'
            else:
                resource.rating += 2 * rating
                msg = f'Рейтинг изменён на {rating}'

            mark_row.mark = rating
    else:
        mark = Mark(file_id=resource.file_id, user_id=user_id, mark=rating)
        session.add(mark)

        resource.rating += rating
        msg = f'Материал оценён на {rating}'

    bot.answer_callback_query(callback_query_id=query.id, text=msg)
    session.commit()


@bot.callback_query_handler(
    lambda query: json.loads(query.data)['action'] == 'download')
def download_file(query):
    user_id = query.from_user.id
    db_file_id = json.loads(query.data)['id']

    if not check_verification(user_id):
        return initiate_registration(user_id, query.from_user)

    file_id = session.query(Resource.file_id) \
        .filter(Resource.id == db_file_id) \
        .scalar()

    bot.send_message(user_id, text=DOWNLOAD_SUCCESS_MSG)
    bot.send_document(user_id, file_id)
    bot.answer_callback_query(callback_query_id=query.id)


def initiate_registration(chat_id, from_user):
    markup = None

    first_name = from_user.first_name
    last_name = from_user.last_name

    if last_name:
        markup = ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row(KeyboardButton(f'{first_name} {last_name}'))

    instruction = bot.send_message(chat_id, NEEDS_REG_MSG, reply_markup=markup)
    return bot.register_next_step_handler(instruction, check_name_surname)


@bot.message_handler(commands=['upload'])
def handle_upload(message):
    chat_id = message.chat.id

    if not check_verification(message.from_user.id):
        return initiate_registration(chat_id, message.from_user)

    instruction = bot.send_message(chat_id, UPLOAD_TITLE_MSG)
    bot.register_next_step_handler(instruction, check_material)


def check_verification(user_id):
    verified = session.query(User.verified) \
        .filter(User.user_id == user_id) \
        .scalar()

    return verified


def check_material(message):
    chat_id = message.chat.id
    author_id = message.from_user.id

    if message.text in COMMANDS:
        return handle_cancel(message, 'загрузки')

    if message.content_type != 'text' or message.text.startswith('/') \
            or not is_title_correct(message):
        instruction = bot.send_message(chat_id, INCORRECT_DATA_MSG)
        return bot.register_next_step_handler(instruction, check_material)

    message.text = escape(message.text)

    global uploading_material
    uploading_material = Resource(title=message.text, author_id=author_id)

    instruction = bot.send_message(chat_id, UPLOAD_COURSE_MSG)
    bot.register_next_step_handler(instruction, check_course)


def check_course(message):
    chat_id = message.chat.id

    if message.text in COMMANDS:
        return handle_cancel(message, 'загрузки')

    if message.content_type != 'text' or message.text.startswith('/') \
            or not is_course_correct(message):
        instruction = bot.send_message(chat_id, INCORRECT_DATA_MSG)
        return bot.register_next_step_handler(instruction, check_course)

    uploading_material.course = message.text

    markup = ReplyKeyboardMarkup(one_time_keyboard=True)
    for subject in SUBJECTS:
        markup.row(KeyboardButton(subject))

    instruction = bot.send_message(chat_id, UPLOAD_SUBJECT_MSG,
                                   reply_markup=markup)
    bot.register_next_step_handler(instruction, check_subject)


def check_subject(message):
    chat_id = message.chat.id

    if message.text in COMMANDS:
        return handle_cancel(message, 'загрузки')

    if message.content_type != 'text' or message.text.startswith('/') \
            or not is_subject_correct(message):
        instruction = bot.send_message(chat_id, INCORRECT_DATA_MSG)
        return bot.register_next_step_handler(instruction, check_subject)

    message.text = remove_emoji(message.text).upper().strip()

    discipline_i = -1
    for i, subject in enumerate(SUBJECTS):
        subject = remove_emoji(subject).upper().strip()
        if subject == message.text:
            discipline_i = i

    uploading_material.discipline = discipline_i

    instruction = bot.send_message(chat_id, UPLOAD_FILE_MSG,
                                   reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(instruction, check_file)


def check_file(message):
    chat_id = message.chat.id

    if message.text in COMMANDS:
        return handle_cancel(message, 'загрузки')

    if message.content_type != 'document' or not is_file_correct(message):
        instruction = bot.send_message(chat_id, INCORRECT_DATA_MSG)
        return bot.register_next_step_handler(instruction, check_file)

    uploading_material.file_id = message.document.file_id
    uploading_material.rating = 0

    session.add(uploading_material)
    session.commit()

    bot.send_message(chat_id, UPLOAD_SUCCESS_MSG)


def check_name_surname(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if message.text in COMMANDS:
        return handle_cancel(message, 'регистрации')

    if message.content_type != 'text' or message.text.startswith('/') \
            or not is_name_surname_correct(message):
        instruction = bot.send_message(chat_id, INCORRECT_DATA_MSG)
        return bot.register_next_step_handler(instruction, check_name_surname)

    message.text = escape(message.text)

    global registering_user
    registering_user = User(user_id=user_id, name=message.text)

    instruction = bot.send_message(chat_id, REG_MAIL_MSG,
                                   reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(instruction, check_email)


def check_email(message):
    chat_id = message.chat.id

    if message.text in COMMANDS:
        return handle_cancel(message, 'регистрации')

    if message.content_type != 'text' or message.text.startswith('/') \
            or not is_email_correct(message):
        instruction = bot.send_message(chat_id, INCORRECT_DATA_MSG)
        return bot.register_next_step_handler(instruction, check_email)

    registering_user.code = str(int.from_bytes(os.urandom(2), "little"))
    registering_user.email = message.text

    send_email(registering_user.email, "Регистрация в боте BaumanLib",
               registering_user.code)

    instruction = bot.send_message(chat_id, REG_CODE_MSG)
    bot.register_next_step_handler(instruction, check_code)


def check_code(message):
    chat_id = message.chat.id

    if message.text in COMMANDS:
        return handle_cancel(message, 'регистрации')

    if message.content_type != 'text' or message.text.startswith('/') \
            or registering_user.code != message.text:
        instruction = bot.send_message(chat_id, INCORRECT_DATA_MSG)
        return bot.register_next_step_handler(instruction, check_code)

    registering_user.verified = True

    session.add(registering_user)
    session.commit()

    bot.send_message(chat_id, REG_SUCCESS_MSG)


@bot.message_handler(commands=['cancel'])
def handle_cancel(message, mode=None):
    chat_id = message.chat.id

    if mode:
        no_keyboard = ReplyKeyboardRemove()
        bot.send_message(chat_id, cancel_msg(mode), reply_markup=no_keyboard)

    call(message)


@bot.message_handler(commands=['about'])
def handle_about(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, ABOUT_MSG, parse_mode='html')


@bot.message_handler(content_types=ALL_CONTENT_TYPES)
def handle_unknown(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, UNKNOWN_CMD_MSG)
