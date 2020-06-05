from config import *


def is_material_correct(message):
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
    if not hasattr(message, 'text'):
        return False

    text = message.text

    if not text.isdigit():
        return False

    return COURSE_MIN <= int(text) <= COURSE_MAX


def is_subject_correct(message):
    if not hasattr(message, 'text'):
        return False

    return message.text.upper() in SUBJECTS


def is_file_correct(message):
    if not hasattr(message, 'text'):
        return False

    text = message.document.mime_type.split('/')
    return len(text) == 2 and text[1] in ALLOWED_EXTENSIONS


def is_name_surname_correct(message):
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
    if not hasattr(message, 'text'):
        return False

    email = message.text

    if '@' not in email:
        return False

    username, domain = email.split('@')

    if not username or not domain:
        return False

    if any(name in username for name in FORBIDDEN_USERNAMES):
        return False

    if domain not in ALLOWED_MAIL_DOMAINS:
        return False

    for c in username + domain:
        if not (c.isdigit() or c.isalpha()):
            return False

    return True
