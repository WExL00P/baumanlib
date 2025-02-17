HELP_MSG = '👋 Хэй! Смотри, вот полный список моих команд:\n\n' \
           '📌 /start – прочти ещё разок небольшую справку обо мне!\n' \
           '📌 /search – найди нужный материал в моей библиотеке!\n' \
           '📌 /upload – загрузи свои материалы, чтобы они были ' \
           'доступны другим!\n' \
           '📌 /myfiles – посмотри свои загруженные материалы!\n' \
           '📌 /about – узнай чуть больше о создателях проекта или ' \
           'оставь отзыв/предложение!\n' \
           '📌 /cancel – передумал? останови процесс ' \
           'поиска/загрузки материалов!\n' \
           '📌 /help – посмотри подробную подсказку по командам, ' \
           'если вдруг что-нибудь забудешь :^)'

START_MSG = 'Привет! Этот бот – база данных по специальности с ' \
            'удобным поиском и рейтингом. Мудл на максималках!\n\n' \
            'Ты можешь:\n\n' \
            '📥 Загружать различные учебные материалы\n' \
            '🔍 Искать уже загруженные материалы\n' \
            '📈 Оценивать загруженные материалы, давая другим ' \
            'возможность находить достойные материалы быстрее\n\n' \
            'Пиши /help, чтобы узнать меня получше!'

SEARCH_MSG = '🔍 Введи поисковый запрос, а я постараюсь тебе помочь!\n\n' \
             'Для выхода из режима поиска введи /cancel'

UNKNOWN_CMD_MSG = '💧 Прости, дружок, я тебя не понимаю :(\n\nИспользуй ' \
                  'всплывающие подсказки или /help, если позабыл, какие ' \
                  'команды тебе доступны!'

NO_RESULTS_MSG = '💧 Упс, похоже, материалов по твоему запросу ещё нет в ' \
                 'моей библиотеке :(\n\nПопробуй переформулировать его или ' \
                 'первым загрузи материал по теме!'

NEEDS_REG_MSG = '❗ Это могут делать только зарегистрированные пользователи!'

REG_NAME_SURNAME_MSG = 'Введи своё имя и фамилию, пожалуйста!\n\n' \
                       'Для выхода из режима регистрации введи /cancel'

INCORRECT_DATA_MSG = 'Упс! Кажется, ты ввёл некорректные данные. ' \
                     'Попробуй ещё разок, пожалуйста.'

ABOUT_MSG = 'Привет! Мы команда WexL00P:\n\n' \
            '👨🏻‍💻 Матвей @kottsovcom\n' \
            '👨🏻‍💻 Даня @daniilporoshin\n' \
            '👨🏼‍💻 Макс @maksim_borisovv\n' \
            '👨🏻‍💻 Кирилл @IgorVitalevich\n' \
            '👩🏻‍💻 Маша @sleepy_owlet\n\n' \
            'Есть предложения или жалобы?\n' \
            'Обращайся, будем рады помочь :)\n\n' \
            '📮 <b>BaumanLibBot by WexL00P 2020</b>'

UPLOAD_TITLE_MSG = '📥 Введи название материала для загрузки'

UPLOAD_COURSE_MSG = 'Теперь укажи курс, к которому относится твой материал'

UPLOAD_SUBJECT_MSG = 'И, наконец, введи название предмета, которому ' \
                     'соответствует твой материал'

UPLOAD_FILE_MSG = 'Отлично! Теперь загрузи файл, а я добавлю его ' \
                  'в свою библиотеку!'

UPLOAD_SUCCESS_MSG = '🌟 Файл успешно загружен! Спасибо, что пополняешь ' \
                     'мою библиотеку!'

REG_MAIL_MSG = 'Отлично! Теперь укажи адрес своей почты в домене bmstu.ru'

REG_CODE_MSG = 'Супер! Я отправил на эту почту специальной код. Напиши ' \
               'его сюда обычным сообщением, чтобы завершить регистрацию'

REG_SUCCESS_MSG = '🌟 Отлично! Теперь ты спокойно можешь загружать свои ' \
                  'материалы!\n\nТолько не используй меня как хранилище ' \
                  'личных файлов и следи за качеством загружаемых ' \
                  'материалов, иначе мне придется тебя заблокировать :('

DOWNLOAD_SUCCESS_MSG = '🌟 Вот твой файл! Пожалуйста, оцени материал, ' \
                       'чтобы улучшить качество поиска ;)'

SEARCH_FOUND_MSG = '✅ Смотри, я нашёл для тебя {} {}!'

SEARCH_FOUND_MANY_MSG = 'Они отсортированы по убыванию рейтинга: лучшие ' \
                        'отображаются снизу, чтобы тебе не пришлось долго ' \
                        'листать наверх :)'

DELETE_SUCCESS_MSG = '✅ Материал успешно удален из моей библиотеки'

CANCEL_MSG = '⛔️ Выход из режима {}'

REG_LIMIT_MSG = '❕ Хэй! Ты чего такой нетерпеливый? Дружок, подожди ' \
                'немножко, пожалуйста, письмо обязательно придёт, не ' \
                'нужно спамить ;)\n\nЕсли все-таки этого не произошло, ' \
                'попробуй еще раз через {} {}'

CODE_LIMIT_MSG = '💧Упс! Ты уже трижды ввёл неверный код :(\n\n' \
                 'Регистрацию придется пройти заново. Только будь ' \
                 'внимательнее, пожалуйста :)'

FILE_NOT_FOUND_MSG = 'Я не смог найти этот материал :( Возможно он был ' \
                     'удален из моей библиотеки'

NOTHING_UPLOADED_MSG = 'Ты пока ничего не загрузил в мою библиотеку :('


def search_found_msg(count: int) -> str:
    """
    Склоняет слова в SEARCH_FOUND_MSG в зависимости от количества
    материалов (именительный падеж)
    :param count: количество материалов
    :return: форматированная строка
    """
    remainder = count % 10

    if 11 <= count <= 19 or remainder == 0:
        noun = 'материалов'
    elif remainder == 1:
        noun = 'материал'
    elif 2 <= remainder <= 4:
        noun = 'материала'
    else:
        noun = 'материалов'

    msg = SEARCH_FOUND_MSG.format(count, noun)

    if count > 1:
        msg += ' ' + SEARCH_FOUND_MANY_MSG

    return msg


def cancel_msg(mode: str) -> str:
    """
    Форматирует CANCEL_MSG
    :param mode: режим, из которого происходит выход
    :return: форматированная строка
    """
    return CANCEL_MSG.format(mode)


def reg_limit_msg(seconds: int) -> str:
    """
    Склоняет слова в REG_LIMIT_MSG в зависимости от количества
    секунд (именительный падеж)
    :param seconds: количество секунд
    :return: форматированная строка
    """
    remainder = seconds % 10

    if 11 <= seconds <= 19 or remainder == 0:
        noun = 'секунд'
    elif remainder == 1:
        noun = 'секунду'
    elif 2 <= remainder <= 4:
        noun = 'секунды'
    else:
        noun = 'секунд'

    return REG_LIMIT_MSG.format(seconds, noun)
