from check_correct import *


class Message:
    def __init__(self, text):
        self.text = text


def test_is_email_correct():
    """
    Выполняет модульное тестирование функции is_email_correct
    """
    assert is_email_correct(Message('')) is False
    assert is_email_correct(Message(' ')) is False
    assert is_email_correct(Message('@')) is False
    assert is_email_correct(Message('@.')) is False
    assert is_email_correct(Message('@s')) is False
    assert is_email_correct(Message('s@s')) is False
    assert is_email_correct(Message('s@s.s')) is False
    assert is_email_correct(Message('sometext')) is False
    assert is_email_correct(Message('sometext@sometext@s')) is False
    assert is_email_correct(Message('student.bmstu.ru')) is False
    assert is_email_correct(Message('@student.bmstu.ru')) is False
    assert is_email_correct(Message('alexodnodvorcev@bmstu.ru')) is True
    assert is_email_correct(Message('kmd19u791@student.bmstu.ru')) is True
