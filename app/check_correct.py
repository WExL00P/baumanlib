import telebot

subjects = ["ПРОГРАММИРОВАНИЕ", "ОСНОВЫ ПРОГРАММНОЙ ИНЖЕНЕРИИ", "ИНОСТРАННЫЙ ЯЗЫК", \
            "ИСТОРИЯ", "ЭЛЕКТИВНЫЙ КУРС ПО ФИЗИЧЕСКОЙ КУЛЬТУРЕ И СПОРТУ", \
            "ФИЗИКА", "ЛИНЕЙНАЯ АЛГЕБРА И ФУНКЦИИ НЕСКОЛЬКИХ ПЕРЕМЕННЫХ", \
            "ИНТЕГРАЛЫ И ДИФФЕРЕНЦИАЛЬНЫЕ УРАВНЕНИЯ"]


def is_material_correct(message):
    text = message.text
    return len(text) < 256 and text[0] != '/'


def is_course_correct(message):
    text = message.text
    if text.isdigit():
        text = int(text)
        return text >= 1 and text <= 6
    else:
        return False


def is_subject_correct(message):
    text = message.text
    return text.upper() in subjects


def is_file_correct(message):
    text = message.document.mime_type.split('/')
    return len(text) == 2 and text[1] in ["docx", "doc", "pdf", "pptx"]


def is_name_surname_correct(message):
    text = message.text.split()
    if len(text) >= 2:
        for i in text:
            if len(i) <= 2:
                return False
    else:
        return False
    return True


def is_email_correct(message):
    text = message.text
    if "@" in text:
        text = text.split('@')
        if len(text) == 2 and text[1] in ["bmstu.ru", "student.bmstu.ru"]:
            for i in text[1]:
                if not (i.isdigit() or i.isalpha()):
                    return False
        else:
            return False
    else:
        return False
    return True