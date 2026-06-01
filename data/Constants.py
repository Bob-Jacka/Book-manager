from typing import Final

BOOK_EXTENSIONS: Final[list[str]] = ['lrf', 'rar', 'zip', 'rtf', 'lit', 'txt', 'txtz', 'text', 'htm', 'xhtm',
                                     'html', 'htmlz', 'xhtml', 'pdf', 'pdb', 'updb', 'pdr', 'prc', 'mobi',
                                     'azw', 'doc', 'epub', 'fb2', 'fbz', 'djv', 'djvu', 'lrx', 'cbr', 'cb7',
                                     'cbz', 'cbc', 'oebzip', 'rb', 'imp', 'odt', 'chm', 'tpz', 'azw1', 'pml',
                                     'pmlz', 'mbp', 'tan', 'snb', 'xps', 'oxps', 'azw4', 'book', 'zbf', 'pobi',
                                     'docx', 'docm', 'md', 'textile', 'markdown', 'ibook', 'ibooks', 'iba',
                                     'azw3', 'ps', 'kepub', 'kfx', 'kpf']
"""
Extensions of the books to be located by listing all files in directory and comparing names.
"""

NON_BOOK_EXTENSIONS: Final[list[str]] = [
    'jpg', 'jpeg', 'gif', 'png', 'bmp',
    'opf', 'swp', 'swo'
]
"""
Other file extensions, not books extensions.
You can also use just 'not in BOOK_EXTENSIONS'
"""

INPUT_SYM: Final[str] = '>> '

CLOSE_MENU_CODE: Final[str] = '666'
"""
Code for close menu functionality
"""

AUTHOR: Final[str] = 'KIRILL'
"""
Also known as Bob-jacka (Cupcake_wrld)
"""

APP_NAME: Final[str] = 'BookManager'
"""
Name of the app
"""

STATIC_CONFIG_NAME: Final[str] = 'config.txt'

STATIC_READ_FILE_NAME: Final[str] = 'read.txt'

STATIC_DIR_NAME_FOR_FAV: Final[str] = 'прочитанные'

APP_VERSION: Final[str] = '6.2.0'

SITE_WITH_COVERS: Final[str] = 'https://book-cover.ru/covers'
