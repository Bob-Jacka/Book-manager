import abc
import datetime
import os
import re
import shutil
from pathlib import Path
from typing import Any

import yadisk
from google.oauth2 import service_account
from googleapiclient.discovery import build

from core.entities.Book_data import Book_data
from core.entities.BotLogger import BotLogger
from core.entities.Formatter import Format
from core.entities.Translator import Translator
from core.other.Utils import str_input_from_user
from data.Constants import (
    STATIC_READ_FILE_NAME,
    NON_BOOK_EXTENSIONS,
    OSType
)
from data.Tokens import TOKEN_YANDEX, TOKEN_GOOGLE
from data.Wrappers import log


class IDevice(abc.ABC):
    """
    Abstract class for support of connected devices.
    Implement Class for your device to use.
    """

    @abc.abstractmethod
    def init_device(self, current_dir) -> None:
        pass

    @abc.abstractmethod
    def get_path(self):
        pass

    @abc.abstractmethod
    def close_connection(self):
        pass

    @abc.abstractmethod
    def start_device(self):
        pass


class Physical_device(IDevice):
    """
    Physically connected via usb device.
    Ex. your Kindle book or your Digma (not Figma) book
    """

    class Book_dir_controller:
        """
        Controller for books actions, Data independent
        """

        class Book_dir_node:
            def __init__(self, dir_name: str):
                """
                Class for directore with books
                :param dir_name: directory name to store in node
                """
                self.dir_name: str = dir_name
                self.book_names: list[str] = list()
                for book in os.listdir():
                    if Physical_device.Book_dir_controller.is_book(book):
                        self.book_names.append(book)

            def list_books_in_node(self):
                print('Directory contains such books:')
                for num, book in enumerate(self.book_names):
                    print(f'{num}: {book}')

            def get_dir_name(self):
                return self.dir_name

            def get_book_names(self):
                return self.book_names

            def get_book_as_a_book_data(self):
                list_to_return: list[Book_data] = list()
                for book in self.book_names:
                    list_to_return.append(Book_data(book_name=book))
                return list_to_return

        # Book dir controller methods:
        def __init__(self, config):
            """
            Class responsible for directory controller
            :param config: file with configuration
            """
            self.dirs: list[Physical_device.Book_dir_controller.Book_dir_node] = list()
            self.local_logger = config.get_logger()
            self.config = config
            for dir_name in os.listdir():  # TODO will be error, wrong directory
                if dir_name.endswith('') and not dir_name.startswith('.'):
                    self.dirs.append(Physical_device.Book_dir_controller.Book_dir_node(dir_name=dir_name))

        # TODO delete later
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
            os_name: str = self.config.get_run_os()

            # Windows branch
            if os_name == OSType.windows_os:
                save_path = Path.home().as_uri() + os.sep + 'Downloads'
                self.local_logger.log('Windows user path to Downloads directory')

            # Linux branch
            elif os_name == OSType.linux_os:
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
                user_choice = str_input_from_user('Do you really want to delete all books data? yes (y) or no (n)')
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

        def create_directory(self, dir_data) -> None:
            """
            Create directory, used in Book_db
            :return: None
            """
            pass

        def creation_date(self, path_to_file: str | os.PathLike) -> str:
            """
            Try to get the date that a file was created, falling back to when it was
            last modified if that isn't possible.
            See http://stackoverflow.com/a/39501288/1709587 for explanation.
            """
            os_name: str = self.config.get_run_os()

            # Windows branch:
            if os_name == OSType.windows_os:
                return str(os.path.getctime(path_to_file))

            # Linux branch:
            elif os_name == OSType.linux_os:
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

    __local_device_logger: BotLogger = None
    __translator: Translator = None
    __book_dir_controller: Book_dir_controller
    __home_directory: str | Path

    def __init__(self, device_path: str | Path, config):
        self.__home_directory = device_path
        self.__init_device_entities()
        self.config = config
        self.__book_dir_controller = self.Book_dir_controller(config)

    def get_path(self) -> str | Path:
        """
        Get device path in system
        """
        return self.__home_directory

    def init_device(self, current_dir) -> None:
        """
        Initialize some useful application variables.
        Contains in base class for strategies
        :return: None
        """
        try:
            self.__local_device_logger.log(f'device initialized in "{current_dir}" path in filesystem')
            self.__local_device_logger.log('Checking for file with read file by default name')
            if os.path.exists(current_dir + STATIC_READ_FILE_NAME):
                self.__local_device_logger.log('Read books file found')
            else:
                self.__local_device_logger.log('Read books file not found')
            self.__local_device_logger.log('App initialized in manual mode')
        except Exception as e:
            raise Exception(f'Init device failed due to {e}.')

    def __init_device_entities(self):
        try:
            self.__local_device_logger = BotLogger()
            self.__translator = Translator()
        except Exception as e:
            raise Exception(f'App initialization failed due to {e}.')

    def start_device(self):
        try:
            pass

        except Exception as e:
            raise Exception(f'Start device functionality failed due to - {e}.')

    def close_connection(self):
        """
        Delete device entities in case of error or finish
        :return: None
        """
        pass


class Virtual_device(IDevice):
    """
    Virtual device, responsible for Yandex or Google Cloud.
    Need to create 1 virtual device for Yandex and 1 for Google Cloud.
    """
    __local_device_logger: BotLogger = None
    __translator: Translator = None
    __client: Any

    def __init__(self, logger, virtual_client):
        self.__client = virtual_client
        self.__local_device_logger = logger

    def init_device(self) -> None:
        pass

    def get_path(self):
        pass

    def list_all_files(self):
        pass

    def close_connection(self):
        """
        Delete device entities in case of error or finish
        :return: None
        """
        pass

    def start_device(self):
        try:
            pass

        except Exception as e:
            raise Exception(f'Start device functionality failed due to - {e}.')

    def __init_device_entities(self):
        try:
            self.__translator = Translator()
        except Exception as e:
            raise Exception(f'App initialization failed due to {e}.')

    @staticmethod
    def create_yandex_virt_device(logger: BotLogger):
        """
        Factory method for creating Yandex based virtual device
        """
        return Virtual_device(logger=logger, virtual_client=yadisk.Client(token=TOKEN_YANDEX))

    @staticmethod
    def create_google_virt_device(logger: BotLogger):
        """
        Factory method for creating Google based virtual device
        """
        SCOPES = ['https://www.googleapis.com/auth/drive']
        SERVICE_ACCOUNT_FILE = TOKEN_GOOGLE

        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        service = build('drive', 'v3', credentials=credentials)

        return Virtual_device(logger=logger, virtual_client=service)
