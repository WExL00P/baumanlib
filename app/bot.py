import os
import telebot
import json
from datetime import datetime
from xml.sax.saxutils import escape
from sqlalchemy import or_, and_
from telebot.types import (
    KeyboardButton, ReplyKeyboardMarkup,
    ReplyKeyboardRemove, InlineKeyboardButton,
    InlineKeyboardMarkup
)
from config import SUBJECTS, COMMANDS
from templates import *
from validators import *
from utils import send_email, ALL_CONTENT_TYPES
from db import (
    session, Resource, Mark, User,
    State, save_state, get_state, clear_state,
    next_step_backend
)


bot = telebot.TeleBot(
    os.getenv('TELEGRAM_TOKEN'),
    next_step_backend=next_step_backend
)


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


def format_material(material):
    return f'<b>{material.title}</b>\n\n' \
        f'{material.discipline}\n' \
        f'🎓 {material.course} курс\n' \
        f'📊 Рейтинг: {material.rating}'


def check_query(message):
    chat_id = message.chat.id

    if message.text in COMMANDS:
        return handle_cancel(message, 'поиска')

    if message.content_type != 'text' or message.text.startswith('/'):
        instruction = bot.send_message(chat_id, INCORRECT_DATA_MSG)
        return bot.register_next_step_handler(instruction, check_query)

    query = f'%{message.text}%'
    resources = session.query(Resource) \
        .filter(or_(Resource.title.ilike(query),
                    Resource.discipline.ilike(query))) \
        .order_by(Resource.rating.asc())

    resources_n = resources.count()

    if resources_n == 0:
        return bot.send_message(chat_id, NO_RESULTS_MSG)

    for r in resources:
        r.views += 1

        result = format_material(r)
        markup = generate_result_markup(r.id)
        bot.send_message(chat_id, result, reply_markup=markup, parse_mode='html')

    session.commit()
    bot.send_message(chat_id, search_found_msg(resources_n))


@bot.callback_query_handler(
    lambda query: json.loads(query.data)['action'] in ['up', 'down'])
def change_rating(query):
    query_json = json.loads(query.data)

    user_id = query.from_user.id
    file_id = query_json['id']
    rating = query_json['value']

    if not check_verification(user_id):
        bot.answer_callback_query(callback_query_id=query.id)
        return initiate_registration(user_id, query.from_user)

    resource = session.query(Resource) \
        .filter(Resource.id == file_id)

    if resource.count() == 0:
        return bot.answer_callback_query(callback_query_id=query.id,
                                         text=FILE_NOT_FOUND_MSG)

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

    markup = generate_result_markup(resource.id)
    bot.edit_message_text(
        format_material(resource),
        parse_mode='html',
        reply_markup=markup,
        chat_id=query.message.chat.id,
        message_id=query.message.message_id
    )

    bot.answer_callback_query(callback_query_id=query.id, text=msg)
    session.commit()


@bot.callback_query_handler(
    lambda query: json.loads(query.data)['action'] == 'download')
def download_file(query):
    user_id = query.from_user.id
    db_file_id = json.loads(query.data)['id']

    if not check_verification(user_id):
        bot.answer_callback_query(callback_query_id=query.id)
        return initiate_registration(user_id, query.from_user)

    resource = session.query(Resource) \
        .filter(Resource.id == db_file_id)

    if resource.count() == 0:
        return bot.answer_callback_query(callback_query_id=query.id,
                                         text=FILE_NOT_FOUND_MSG)

    resource = resource.one()
    resource.downloads += 1
    session.commit()

    bot.send_message(user_id, text=DOWNLOAD_SUCCESS_MSG)
    bot.send_document(user_id, resource.file_id)
    bot.answer_callback_query(callback_query_id=query.id)


def initiate_registration(chat_id, from_user):
    markup = None

    state = get_state(chat_id)
    if not state:
        state = State()

    first_name = from_user.first_name
    last_name = from_user.last_name

    bot.send_message(chat_id, NEEDS_REG_MSG)

    if state.last_email_date and state.email_attempt > MAX_NO_LIMIT_ATTEMPTS:
        seconds_passed = (datetime.now() - state.last_email_date).seconds
        seconds_left = EMAIL_LIMIT - seconds_passed

        if seconds_left > 0:
            return bot.send_message(chat_id, reg_limit_msg(seconds_left))

    if last_name:
        markup = ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.row(KeyboardButton(f'{first_name} {last_name}'))

    save_state(chat_id, state)

    instruction = bot.send_message(chat_id, REG_NAME_SURNAME_MSG,
                                   reply_markup=markup)
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

    state = get_state(chat_id)
    if not state:
        state = State()

    state.uploading_material = Resource(title=message.text,
                                                  author_id=author_id)

    save_state(chat_id, state)

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

    state = get_state(chat_id)
    state.uploading_material.course = message.text

    markup = ReplyKeyboardMarkup(one_time_keyboard=True)
    for subject in SUBJECTS:
        markup.row(KeyboardButton(subject))

    save_state(chat_id, state)

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

    state = get_state(chat_id)
    state.uploading_material.discipline = message.text

    save_state(chat_id, state)

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

    state = get_state(chat_id)
    uploading_material = state.uploading_material

    uploading_material.file_id = message.document.file_id
    uploading_material.rating = 0
    uploading_material.views = 0
    uploading_material.downloads = 0

    session.add(uploading_material)
    session.commit()

    # Закончили — можем отчистить состояние
    clear_state(chat_id)

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

    state = get_state(chat_id)
    if not state:
        state = State()

    state.registering_user = User(user_id=user_id, name=message.text)
    save_state(chat_id, state)

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

    state = get_state(chat_id)

    state.registering_user.code = str(int.from_bytes(os.urandom(2), 'little'))
    state.registering_user.email = message.text

    # ставим статус боту, пока письмо отправляется
    bot.send_chat_action(chat_id, 'typing')

    send_email(state.registering_user.email, 'Регистрация в боте BaumanLib',
               state.registering_user.code)

    state.last_email_date = datetime.now()
    state.email_attempt += 1

    save_state(chat_id, state)

    instruction = bot.send_message(chat_id, REG_CODE_MSG)
    bot.register_next_step_handler(instruction, check_code)


def check_code(message):
    chat_id = message.chat.id

    if message.text in COMMANDS:
        return handle_cancel(message, 'регистрации')

    state = get_state(chat_id)
    registering_user = state.registering_user

    if message.content_type != 'text' or message.text.startswith('/') \
            or registering_user.code != message.text:
        instruction = bot.send_message(chat_id, INCORRECT_DATA_MSG)
        return bot.register_next_step_handler(instruction, check_code)

    registering_user.verified = True

    session.add(registering_user)
    session.commit()

    # Закончили — можем отчистить состояние
    clear_state(chat_id)

    bot.send_message(chat_id, REG_SUCCESS_MSG)


@bot.message_handler(commands=['cancel'])
def handle_cancel(message, mode=None):
    chat_id = message.chat.id

    clear_state(chat_id)

    if mode:
        no_keyboard = ReplyKeyboardRemove()
        bot.send_message(chat_id, cancel_msg(mode), reply_markup=no_keyboard)

    call(message)


def generate_control_markup(material_id):
    markup = InlineKeyboardMarkup()

    del_data = json.dumps({'action': 'delete', 'id': material_id})
    del_btn = InlineKeyboardButton(text='Удалить', callback_data=del_data)

    markup.add(del_btn)
    return markup


@bot.message_handler(commands=['myfiles'])
def handle_myfiles(message):
    chat_id = message.chat.id

    if not check_verification(message.from_user.id):
        return initiate_registration(chat_id, message.from_user)

    files = session.query(Resource) \
        .filter(Resource.author_id == message.from_user.id)

    if files.count() == 0:
        return bot.send_message(chat_id, NOTHING_UPLOADED_MSG)

    for file in files:
        result = format_material(file)
        result += f'\n👀 Просмотров: {file.views}\n' \
                  f'📥 Скачиваний: {file.downloads}'

        markup = generate_control_markup(file.id)
        bot.send_message(chat_id, result, parse_mode='html', reply_markup=markup)


@bot.callback_query_handler(
    lambda query: json.loads(query.data)['action'] == 'delete')
def delete_material(query):
    user_id = query.from_user.id
    db_file_id = json.loads(query.data)['id']

    if not check_verification(user_id):
        bot.answer_callback_query(callback_query_id=query.id)
        return initiate_registration(user_id, query.from_user)

    resource = session.query(Resource) \
        .filter(and_(Resource.id == db_file_id, Resource.author_id == user_id))

    if resource.count() == 0:
        return bot.answer_callback_query(callback_query_id=query.id,
                                         text=FILE_NOT_FOUND_MSG)

    resource.delete()
    session.commit()

    bot.send_message(user_id, text=DELETE_SUCCESS_MSG)
    bot.answer_callback_query(callback_query_id=query.id)


@bot.message_handler(commands=['about'])
def handle_about(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, ABOUT_MSG, parse_mode='html')


@bot.message_handler(content_types=ALL_CONTENT_TYPES)
def handle_unknown(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, UNKNOWN_CMD_MSG)
