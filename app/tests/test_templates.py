from templates import *


def test_search_found_msg():
    """
    Выполняет модульное тестирование функции search_found_msg
    """
    assert search_found_msg(0) == SEARCH_FOUND_MSG.format('0', 'материалов')
    assert search_found_msg(1) == SEARCH_FOUND_MSG.format('1', 'материал')

    combined = SEARCH_FOUND_MSG + ' ' + SEARCH_FOUND_MANY_MSG

    for i in range(2, 5):
        assert search_found_msg(i) == combined.format(str(i), 'материала')

    for i in range(10, 20):
        assert search_found_msg(i) == combined.format(str(i), 'материалов')

    assert search_found_msg(101) == combined.format('101', 'материал')
    assert search_found_msg(105) == combined.format('105', 'материалов')


def test_reg_limit_msg():
    """
    Выполняет модульное тестирование функции reg_limit_msg
    """
    assert reg_limit_msg(0) == REG_LIMIT_MSG.format('0', 'секунд')
    assert reg_limit_msg(1) == REG_LIMIT_MSG.format('1', 'секунду')

    for i in range(2, 5):
        assert reg_limit_msg(i) == REG_LIMIT_MSG.format(str(i), 'секунды')

    for i in range(10, 20):
        assert reg_limit_msg(i) == REG_LIMIT_MSG.format(str(i), 'секунд')

    assert reg_limit_msg(101) == REG_LIMIT_MSG.format('101', 'секунду')
    assert reg_limit_msg(105) == REG_LIMIT_MSG.format('105', 'секунд')


def test_cancel_msg():
    """
    Выполняет модульное тестирование функции cancel_msg
    """
    assert cancel_msg('а') == CANCEL_MSG.format('а')
    assert cancel_msg('регистрации') == CANCEL_MSG.format('регистрации')
