import telebot

subjects = ["ПРОГРАММИРОВАНИЕ", "ОСНОВЫ ПРОГРАММНОЙ ИНЖЕНЕРИИ", "ИНОСТРАННЫЙ ЯЗЫК", /
            "ИСТОРИЯ", "ЭЛЕКТИВНЫЙ КУРС ПО ФИЗИЧЕСКОЙ КУЛЬТУРЕ И СПОРТУ", /
            "ФИЗИКА", "ЛИНЕЙНАЯ АЛГЕБРА И ФУНКЦИИ НЕСКОЛЬКИХ ПЕРЕМЕННЫХ", /
            "ИНТЕГРАЛЫ И ДИФФЕРЕНЦИАЛЬНЫЕ УРАВНЕНИЯ"]


def is_material_correct(message):
    text = message.text
    if (len(text) >= 256):
        return False
    else:
        return True

def is_course_correct(message):
    text = message.text
    if text.isdigit():
        text = int(text)
        if text >= 1 and text <= 6:
            return True
        else:
            return False
    else:
        return False

def is_subject_correct(message):
    text = message.text
    if text.isdigit():
        text = int(text)
        if text >= 1 and text <= 8:
            return True
        else:
            return False
    else:
        return False

def is_file_correct(message):
    text = message.document.mime_type.split('/')
    if len(text) == 2 and text[1] in ["docx", "doc", "pdf", "pptx"]:
        return True
    else:
        return False

def is_name_surname_correct(message):
    text = message.text.split()
    if len(text) >= 2:
        for str in text:
            if len(str) <= 2:
                return False
    else:
        return False
    return True

def is_email_correct(message):
    text = message.text
    if "@" in text:
        text = text.split('@')
        if len(text) == 2 and text[1] in ["bmstu.ru", "student.bmstu.ru"]:
            for x in text[1]:
                if not (x.isdigit() or x.isalpha()):
                    return False
        else:
            return False
    else:
        return False
    return True