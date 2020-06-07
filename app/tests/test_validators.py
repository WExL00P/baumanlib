from validators import *


class Document:
    def __init__(self):
        self.mime_type = None


class Message:
    def __init__(self, text):
        self.text = text
        self.document = None


def test_is_title_correct():
    """
    Выполняет модульное тестирование функции is_title_correct
    """
    assert is_title_correct('') is False
    assert is_title_correct(Message('')) is False
    assert is_title_correct(Message('  ')) is False
    assert is_title_correct(Message('/')) is False
    assert is_title_correct(1488) is False
    assert is_title_correct(Message('235628')) is False
    assert is_title_correct(Message('Sweet dreams are made of this')) is True
    assert is_title_correct(Message('Who am I 2 disagree')) is True
    assert is_title_correct(Message('wexloop')) is True
    assert is_title_correct(Message('погроммирование.бмсту')) is True
    assert is_title_correct(Message('Самбади ванс толд ми зэ ворлд из гонна '
                                    'ролл ми ай эйнт зэ шарпест тул ин зэ шэд '
                                    'щи воз лукин кайнда дамб виз хер фингер '
                                    'энд хер тамб ин зэ шейп оф ан эл он хёр '
                                    'фохэд вэлл зэ ерс старт каминг энд зэй '
                                    'донт стап камин фед ту зэ рулз энд ай '
                                    'хит зэ граунд раннинг')) is False


def test_is_course_correct():
    """
    Выполняет модульное тестирование функции is_course_correct
    """
    assert is_course_correct('') is False
    assert is_course_correct(Message('')) is False
    assert is_course_correct(Message('  ')) is False
    assert is_course_correct(Message('/')) is False
    assert is_course_correct(1488) is False
    assert is_course_correct(Message('букавки')) is False
    assert is_course_correct(Message('0')) is False
    assert is_course_correct(Message('-1')) is False
    assert is_course_correct(Message('-789009777675')) is False
    assert is_course_correct(Message('2.5')) is False
    assert is_course_correct(Message('2/')) is False
    assert is_course_correct(Message('два')) is False
    assert is_course_correct(Message('342893939')) is False
    assert is_course_correct(Message('    4    ')) is False
    assert is_course_correct(Message('6')) is True
    assert is_course_correct(Message('1')) is True


def test_is_subject_correct():
    """
    Выполняет модульное тестирование функции is_subject_correct
    """
    assert is_subject_correct('') is False
    assert is_subject_correct(Message('')) is False
    assert is_subject_correct(Message('  ')) is False
    assert is_subject_correct(Message('/')) is False
    assert is_subject_correct(1488) is False
    assert is_subject_correct(Message('67')) is False
    assert is_subject_correct(Message(':^)')) is False
    assert is_subject_correct(Message('История;)')) is False
    assert is_subject_correct(Message('Мотемотика')) is False
    assert is_subject_correct(Message('Программирование')) is True
    assert is_subject_correct(Message('ПРОГРАММИРОВАНИЕ')) is True


def test_is_name_surname_correct():
    """
    Выполняет модульное тестирование функции is_name_surname_correct
    """
    assert is_name_surname_correct('') is False
    assert is_name_surname_correct(Message('')) is False
    assert is_name_surname_correct(Message('  ')) is False
    assert is_name_surname_correct(Message('/')) is False
    assert is_name_surname_correct(1488) is False
    assert is_name_surname_correct(Message('128')) is False
    assert is_name_surname_correct(Message('(^:)')) is False
    assert is_name_surname_correct(Message('П')) is False
    assert is_name_surname_correct(Message('Пум-пум')) is False
    assert is_name_surname_correct(Message('Пум-пурум.Пам-парам;')) is False
    assert is_name_surname_correct(Message('h e l l o')) is False
    assert is_name_surname_correct(Message('Пам папам12')) is True
    assert is_name_surname_correct(Message('Пум-пум Пум-пурум')) is True
    assert is_name_surname_correct(Message('Пу Руру')) is True


def test_is_email_correct():
    """
    Выполняет модульное тестирование функции is_email_correct
    """
    assert is_email_correct('') is False
    assert is_email_correct(Message('')) is False
    assert is_email_correct(Message(' ')) is False
    assert is_email_correct(Message('@')) is False
    assert is_email_correct(Message('@.')) is False
    assert is_email_correct(1488) is False
    assert is_email_correct(Message('@s')) is False
    assert is_email_correct(Message('s@s')) is False
    assert is_email_correct(Message('s@s.s')) is False
    assert is_email_correct(Message('all@student.bmstu.ru')) is False
    assert is_email_correct(Message('sometext')) is False
    assert is_email_correct(Message('sometext@sometext@s')) is False
    assert is_email_correct(Message('student.bmstu.ru')) is False
    assert is_email_correct(Message('@student.bmstu.ru')) is False
    assert is_email_correct(Message('alexodnodvorcev@bmstu.ru')) is True
    assert is_email_correct(Message('kmd19u791@student.bmstu.ru')) is True


def test_is_file_correct():
    """
    Выполняет модульное тестирование функции is_file_correct
    """
    assert is_file_correct('') is False

    message = Message('hello')
    assert is_file_correct(message) is False

    message.document = Document()
    message.document.mime_type = 'a'
    assert is_file_correct(message) is False

    message.document.mime_type = '/'
    assert is_file_correct(message) is False

    message.document.mime_type = 'a/'
    assert is_file_correct(message) is False

    message.document.mime_type = 'a/b'
    assert is_file_correct(message) is False

    message.document.mime_type = 'image/png'
    assert is_file_correct(message) is False

    message.document.mime_type = 'application/pdf'
    assert is_file_correct(message) is True


def test_is_text():
    """
    Выполняет модульное тестирование функции is_text
    """
    assert is_text('') is False
    assert is_text('hello') is False
    assert is_text(Message('/hello')) is False
    assert is_text(Message('o')) is False

    valid_text = Message('o')
    valid_text.content_type = 'text'

    assert is_text(valid_text) is True
