"""
Kindle history module

Responsible for local storage of history (on e-book device) and on remote targets
"""

import os

from core.entities.AbstractModule import Module
from core.entities.Book_data import Book_data
from data.Wrappers import log


class Kindle_history(Module):

    def __init__(self):
        self.config = None
        self.local_logger = None
        self.readFile = None

    @log
    def post_init(self, app_config):
        self.config = app_config
        self.local_logger = app_config.get_logger()
        self.readFile = app_config.get_read_file_name()

    def __parse_line(self, line: str) -> dict[str, str]:
        """
        Split line into map, ex. <book name>|<book author>|<book release year>
        :param line: line of book text
        :return: dict with data
        """
        split_line = line.split('|')
        to_return: dict[str, str] = dict()
        if len(split_line) < 5 and len(split_line) == 1:  # case of no such format
            to_return['name'] = str(split_line)
            to_return['author'] = '-'
            to_return['date'] = '-'
            to_return['when_read'] = '-'
            to_return['type'] = '-'
            self.local_logger.log('Wrong format string in parsing found')
            return to_return
        else:
            to_return['name'] = split_line[0]
            to_return['author'] = split_line[1]
            to_return['date'] = split_line[2]
            to_return['when_read'] = split_line[3]
            to_return['type'] = split_line[4]
            return to_return

    @log
    def get_config(self):
        return self.config

    @log
    def list_all_read_book(self) -> list[dict]:
        """
        Function for output all books that have been red.
        outputs only files with books extensions.
        :return: None
        """
        list_with_history: list[dict] = []
        with open(self.config.path_to_read_file()) as file_with_history:
            for line in file_with_history:
                list_with_history.append(self.__parse_line(line))
        return list_with_history

    @log
    def list_favourite_books(self) -> list[dict]:
        """
        Function for listing favourite books (books that saved in home directory)
        :return: None
        """
        fav_books: list[dict] = list()
        stored_fav_books = os.listdir(self.config.path_to_stored_books())
        if len(stored_fav_books) == 0:
            return []
        else:
            for stored_book in stored_fav_books:
                fav_books.append(self.__parse_line(stored_book))
            if len(fav_books) != 0:
                return fav_books
            else:
                return []

    @log
    def add_book_to_history(self, book: Book_data):
        """
        :param book: where first argument is path to book and second argument is book name
        :return: None
        """
        if book is not None:
            return self.memorize_module.add(book, 'only-local')
        else:
            self.local_logger.log('Failed to add book into history')
            return False

    @log
    def count_all_books(self) -> tuple[list[dict], list[dict], int]:
        """
        Function for count books in read file if exists
        :return: book count
        """
        all_books: list[dict] = self.list_all_read_book()
        fav_books: list[dict] = self.list_favourite_books()
        count = len(all_books) + len(fav_books)
        return tuple((all_books, fav_books, count))

    @log
    def find_book(self, book_to_find: str) -> bool | None:
        """
        Function for finding book in read file, by providing book name or name part.
        :return: None
        """
        return self.memorize_module.find(book_to_find, 'only-local')

    @log
    def check_for_duplicates(self) -> None:
        """
        Check for duplicates in read file and output useful message about
        :return: None
        """
        all_data = self.readFile.readlines()
        is_found: bool = False
        for book_name in all_data:
            count = all_data.count(book_name)
            if count >= 2:
                is_found = True
                self.local_logger.log(f'Duplicate found with name {book_name} for {count} times')
        if not is_found:
            self.local_logger.log('No duplicates found')

    @log
    def is_need_for_new_line(self) -> bool:
        """
        Super dummy function for checking if you need new line symbol in read file.
        :return: bool value if you need for new line in read file
        """
        books_counter: int = 0
        new_line_counter: int = 0
        lines = open(self.config.path_to_read_file).readlines()
        while True:
            file_lines = lines[books_counter]
            if file_lines.endswith('\n'):
                new_line_counter += 1

            if file_lines == '':
                break

            books_counter += 1
        if books_counter > new_line_counter:
            return True
        elif books_counter == new_line_counter:
            return False
        else:
            return False
