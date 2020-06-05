COMMANDS = ['/start', '/help', '/search', '/about', '/upload', '/cancel']

SUBJECTS = [
    'ПРОГРАММИРОВАНИЕ',
    'ОСНОВЫ ПРОГРАММНОЙ ИНЖЕНЕРИИ',
    'ИНОСТРАННЫЙ ЯЗЫК',
    'ИСТОРИЯ',
    'ЭЛЕКТИВНЫЙ КУРС ПО ФИЗИЧЕСКОЙ КУЛЬТУРЕ И СПОРТУ',
    'ФИЗИКА',
    'ЛИНЕЙНАЯ АЛГЕБРА И ФУНКЦИИ НЕСКОЛЬКИХ ПЕРЕМЕННЫХ',
    'ИНТЕГРАЛЫ И ДИФФЕРЕНЦИАЛЬНЫЕ УРАВНЕНИЯ'
]

ALLOWED_EXTENSIONS = ['docx', 'doc', 'pdf', 'pptx']

ALLOWED_MAIL_DOMAINS = ['student.bmstu.ru', 'bmstu.ru']
FORBIDDEN_MAIL_NAMES = ['all', 'group']

COURSE_MIN = 1
COURSE_MAX = 6

MAX_TITLE_LENGTH = 256
