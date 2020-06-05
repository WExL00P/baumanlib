COMMANDS = ['/start', '/help', '/search', '/about', '/upload', '/cancel']

SUBJECTS = [
    '💻 Программирование',
    '📁 Основы программной инженерии',
    '📘 Иностранный язык',
    '⚖️ История',
    '🚴 Элективный курс по физической культуре и спорту',
    '🔭 Физика',
    '📈 Линейная алгебра и функции нескольких переменных',
    '📊 Интегралы и дифференциальные уравнения'
]

ALLOWED_EXTENSIONS = ['docx', 'doc', 'pdf', 'pptx']

ALLOWED_MAIL_DOMAINS = ['student.bmstu.ru', 'bmstu.ru']
FORBIDDEN_MAIL_NAMES = ['all', 'group']

COURSE_MIN = 1
COURSE_MAX = 6

MAX_TITLE_LENGTH = 256
