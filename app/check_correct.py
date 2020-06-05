from config import *
from email_validator import validate_email, EmailNotValidError


def is_title_correct(message):
    """
    Проверяет корректность введенного описания материала
    :param message: сообщение пользователя с описанием материала
    :return: является ли описание корректным или нет
    """
    if not hasattr(message, 'text'):
        return False

    text = message.text

    if len(text) >= MAX_TITLE_LENGTH:
        return False

    for c in text:
        if c.isalpha():
            return True

    return False


def is_course_correct(message):
    """
    Проверяет корректность введенного курса
    :param message: сообщение пользователя с номером курса
    :return: является ли курс корректным или нет
    """
    if not hasattr(message, 'text'):
        return False

    text = message.text

    if not text.isdigit():
        return False

    return COURSE_MIN <= int(text) <= COURSE_MAX


def is_subject_correct(message):
    """
    Проверяет корректность введенного предмета
    :param message: сообщение пользователя с названием предмета
    :return: является ли предмет корректным или нет
    """
    if not hasattr(message, 'text'):
        return False

    return message.text.upper() in SUBJECTS


def is_file_correct(message):
    """
    Проверяет корректность отправленного пользователем файла
    :param message: сообщение пользователя с файлом
    :return: является ли файл корректным или нет
    """
    if not hasattr(message, 'text'):
        return False

    kind, extension = message.document.mime_type.split('/')

    if not extension:
        return False

    return extension in ALLOWED_EXTENSIONS


def is_name_surname_correct(message):
    """
    Проверяет корректность имени, фамилии пользователя
    :param message: сообщение пользователя с именем и фамилией
    :return: является ли имя, фамилия корректными или нет
    """
    if not hasattr(message, 'text'):
        return False

    text = message.text.split()

    if len(text) < 2:
        return False

    for c in text:
        if len(c) <= 2:
            return False

    return True


def is_email_correct(message):
    """
    Проверяет корректность адреса почты и ее принадлежность
    студенту МГТУ им. Н.Э. Баумана
    :param message: сообщение пользователя с адресом почты
    :return: является ли почта корректной или нет
    """
    if not hasattr(message, 'text'):
        return False

    try:
        valid = validate_email(message.text)
    except EmailNotValidError:
        return False

    if any(name in valid.ascii_local_part for name in FORBIDDEN_MAIL_NAMES):
        return False

    return valid.ascii_domain in ALLOWED_MAIL_DOMAINS
