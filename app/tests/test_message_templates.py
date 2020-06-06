from message_templates import *


def test_search_found_msg():
    assert search_found_msg(0) == SEARCH_FOUND_MSG.format('0', 'материалов')
    assert search_found_msg(1) == SEARCH_FOUND_MSG.format('1', 'материал')

    combined = SEARCH_FOUND_MSG + ' ' + SEARCH_FOUND_MANY_MSG

    for i in range(2, 5):
        assert search_found_msg(i) == combined.format(str(i), 'материала')

    for i in range(10, 20):
        assert search_found_msg(i) == combined.format(str(i), 'материалов')

    assert search_found_msg(101) == combined.format('101', 'материал')
    assert search_found_msg(105) == combined.format('105', 'материалов')
