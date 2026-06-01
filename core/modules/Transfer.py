import datetime
import os
import platform
import re
import shutil
from enum import Enum
from pathlib import Path

from core.entities.AbstractModule import Module
from core.entities.Book_data import Book_data
from core.entities.Formatter import Format
from data.Constants import (
    NON_BOOK_EXTENSIONS,
    INPUT_SYM
)
from data.Wrappers import log


class OSType(Enum):
    """
    Enum with os identifiers that allowed in utility
    """
    windows_os = 'Windows',
    linux_os = 'Linux',
    mac_os = 'Mac_os'


class Book_dir_node:
    def __init__(self, dir_name: str):
        """
        Class for directore with books
        :param dir_name: directory name to store in node
        """
        self.dir_name: str = dir_name
        self.book_names: list[str] = list()
        for book in os.listdir():
            if Book_dir_controller.is_book(book):
                self.book_names.append(book)

    def list_books_in_node(self):
        print('Directory contains such books:')
        counter = 0
        for book in self.book_names:
            print(f'{counter}: {book}')
            counter += 1

    def get_dir_name(self):
        return self.dir_name

    def get_book_names(self):
        return self.book_names

    def get_book_as_a_book_data(self):
        list_to_return: list[Book_data] = list()
        for book in self.book_names:
            list_to_return.append(Book_data(book_name=book))
        return list_to_return


class Book_dir_controller:
    """
    Controller for books actions, Data independent
    """

    def __init__(self, config):
        """
        Class responsible for directory controller
        :param config: file with configuration
        """
        self.dirs: list[Book_dir_node] = list()
        self.local_logger = config.get_logger()
        self.config = config
        for dir_name in os.listdir():
            if dir_name.endswith('') and not dir_name.startswith('.'):
                self.dirs.append(Book_dir_node(dir_name=dir_name))

    def list_nodes(self):
        print('Utility contains such directories with books:')
        dir_counter: int = 0
        for node in self.dirs:
            print(f'{dir_counter}: {node}')

    def list_nodes_with_books(self):
        print('Utility contains such directories with books:')
        dir_counter: int = 0
        for node in self.dirs:
            print(f'{dir_counter}: {node}')
            node.list_books_in_node()

    def do_backup_copy(self) -> None:
        """
        Function for backup your books in given directory (Download dir).
        :return: None
        """
        self.local_logger.log('Backup books invoked')
        save_path: str | os.PathLike
        if platform.system() == OSType.windows_os:
            save_path = Path.home().as_uri() + os.sep + 'Downloads'
            self.local_logger.log('Windows user path to Downloads directory')
        elif platform.system() == OSType.linux_os:
            save_path = Path.home().as_uri() + os.sep + 'Downloads'
            self.local_logger.log('Linux user path to Downloads directory')
        else:
            raise Exception('Unknown operating system, not implemented yet.')

        for dir in os.listdir():
            self.copy_fs_entity(dir, save_path)
            self.local_logger.log(f'File - {dir} backed up in {save_path}')

    def reset_data(self) -> None:
        """
        Method for deleting all book data (exclude file with book read).
        Also home directory of the app will be saved.
        :return: None
        """
        while True:
            print('Do you really want to delete all books data? yes (y) or no (n)')
            user_choice = input(INPUT_SYM)
            if user_choice == 'yes' or user_choice == 'y':
                self.local_logger.log('Reset data is invoked')
                for dir in self.dirs:
                    self.delete_fs_entity(dir.get_dir_name())
            elif user_choice == 'no' or user_choice == 'n':
                self.local_logger.log('Reset data canceled')
            else:
                print('Wrong choice, try again')
                continue

    def delete_fs_entity(self, path: str | os.PathLike) -> None:
        """
        Function for deleting book in given path, also can delete directory with save points;
        :param path: path to book
        :return: None
        """
        self.local_logger.log('Delete fs entity invoked')
        if path is not None:

            # file branch
            if os.path.isfile(path):
                try:
                    if path.endswith(self.config.path_to_read_file):
                        self.local_logger.log('You cannot delete your read file!')
                    else:
                        os.remove(path)
                        Format.prGreen('Book deleted from directory')
                except Exception as e:
                    self.local_logger.log(f'Exception occurred in deleting book in {path} - {e}')

            # directory branch
            elif os.path.isdir(path):
                try:
                    shutil.rmtree(path)
                    Format.prGreen(f'Directory {path} deleted')
                except Exception as e:
                    self.local_logger.log(f'Exception occurred in deleting directory in {path} - {e}')
        else:
            self.local_logger.log('Path cannot be None')

    def copy_fs_entity(self, path: str | os.PathLike, dir_name: str = '') -> None:
        """
        Save your book in central directory (app installation home).
        :param path: path from where you want to copy read book.
        :param dir_name: *optional parameter, special for directory copying. Use for creating new directory and copy all into
        :return: None
        """
        self.local_logger.log('Copy fs entity invoked')
        central_dir = self.config.get_central_dir_name()
        if path is not None:

            # file branch
            if os.path.isfile(path):
                try:
                    shutil.copy2(path, central_dir)  # {src} {dest}
                    Format.prGreen('Book save in central directory')
                except Exception as e:
                    self.local_logger.log(f'Error occurred while saving book in central dir - {e}')

            # directory branch
            elif os.path.isdir(path):
                try:
                    new_save_point_path = central_dir + os.sep + dir_name
                    os.mkdir(new_save_point_path)  # create new directory, instead of deleting old
                    shutil.copytree(path, new_save_point_path, dirs_exist_ok=True)  # {src} {dest}
                    Format.prGreen('Directory save in central directory')
                except Exception as e:
                    self.local_logger.log(f'Error occurred while saving directory in central dir - {e}')

            else:
                Format.prRed('Object type nor file or directory')
                raise Exception(f'Cannot determine object type of {path}')
            self.delete_fs_entity(path)
        else:
            self.local_logger.log('Path cannot be None')

    def create_directory(self, dir_data):
        """
        Create directory, used in Book_db
        :return:
        """
        pass

    def creation_date(self, path_to_file: str | os.PathLike) -> str:
        """
        Try to get the date that a file was created, falling back to when it was
        last modified if that isn't possible.
        See http://stackoverflow.com/a/39501288/1709587 for explanation.
        """
        if platform.system() == OSType.windows_os:
            return str(os.path.getctime(path_to_file))
        elif platform.system() == OSType.linux_os:
            try:
                mtime = os.path.getmtime(path_to_file)
                mtime_readable = datetime.date.fromtimestamp(mtime)
                return str(mtime_readable)
            except AttributeError:
                return str(datetime.datetime.now())
        else:
            raise NotImplemented('It seems that you have Mac operating system, not implemented for this system')

    @staticmethod
    def is_book(name: str) -> bool:
        """
        Function for filtering directory for books
        :param name: name of the file to proceed
        :return: bool value, if name ended with 'book' extensions.
        """
        ext = os.path.splitext(name)[1]
        if not ext:
            return False
        ext = ext[1:].lower()
        bad_ext_pat = re.compile(r'[^a-z0-9_]+')
        if ext in NON_BOOK_EXTENSIONS or bad_ext_pat.search(ext) is not None:
            return False
        return True

    def check_for_not_started(self):
        """
        Collect information about books that were not started and print them in console
        :return: None
        """
        pass

    def check_for_started(self):
        """
        Collect information about books that were started and print them in console
        :return: None
        """
        pass

    def count_books(self):
        counter: int = 0
        for dir in self.dirs:
            for _ in dir.get_book_names():
                counter += 1


class Transfer(Module):

    def run_module_web(self) -> None:
        pass

    def __init__(self):
        self.config = None
        self.local_logger = None
        self.book_dir_controller = None

    @log
    def post_init(self, app_config):
        self.config = app_config
        self.local_logger = app_config.get_logger()
        self.book_dir_controller = Book_dir_controller(app_config)

    @log
    def add_new_book(self, book: Book_data) -> None:
        """
        Add new book for auto processing.
        :param book: book object to add
        :return: None
        """
        if book is not None:
            try:
                book_name: str  # name of the book to proceed
                if self.readFile is not None:
                    self.readFile.add_book(book)
                    self.book_dir_controller.copy_fs_entity(book.get_full_path())
                    self.book_dir_controller.copy_fs_entity(book.get_save_point_path(),
                                                            dir_name=book.get_save_point_name())
                    self.local_logger.log('Save points also saved')
                    self.book_dir_controller.delete_fs_entity(
                        book.get_full_path()
                    )  # delete book if you not want to save it
                else:
                    self.book_dir_controller.delete_fs_entity(book.get_full_path())

            except Exception as e:
                self.local_logger.log(f'Exception while adding new book - {e}')
