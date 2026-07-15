from pathlib import Path
from typing import Any, override, Literal

import yadisk
from google.oauth2 import service_account
from googleapiclient.discovery import build

from core.entities.Book_data import Book_data
from core.entities.BotLogger import BotLogger
from core.entities.Translator import Translator
from core.entities.device.Code_handler import manual_code_receive
from core.entities.device.IDevice import IDevice, IBookable, IClient
from data.Constants import VIRTUAL_START_PATH

try:
    from data.Tokens import TOKEN_GOOGLE
except FileNotFoundError:
    raise Exception('Create Tokens file in data directory and provide tokens')


class Client(IBookable, IClient):
    """
    Client Abstraction for virtual devices
    """

    __type: Literal['yandex', 'google']
    __underlying_client: Any

    def __init__(self, virtual_client, client_type: Literal['yandex', 'google'], client_home_path: str):
        self.__type = client_type
        self.__underlying_client = virtual_client
        self.client_home_path = client_home_path
        if self.__type == 'yandex':
            if self.__underlying_client.exists(VIRTUAL_START_PATH):
                self.client_home_path = VIRTUAL_START_PATH
            else:
                self.__underlying_client.mkdir(VIRTUAL_START_PATH)
                self.client_home_path = VIRTUAL_START_PATH

        elif self.__type == 'google':
            raise NotImplementedError('Implement functionality first')
        else:
            raise NotImplementedError('Implement functionality first')

    @override
    def check_client(self) -> bool | None:
        if self.__type == 'yandex':
            with self.__underlying_client as client:
                return True  # TODO may cause problems
        elif self.__type == 'google':
            raise NotImplementedError('Implement functionality first')
        else:
            raise NotImplementedError('Implement functionality first')

    @override
    def init_connection(self) -> None:
        if self.__type == 'yandex':
            with self.__underlying_client as client:
                pass
        elif self.__type == 'google':
            raise NotImplementedError('Implement functionality first')
        else:
            raise NotImplementedError('Implement functionality first')

    @override
    def check_path(self, path_to_check: str) -> bool | None:
        if self.__type == 'yandex':
            with self.__underlying_client as client:
                pass
        elif self.__type == 'google':
            raise NotImplementedError('Implement functionality first')
        else:
            raise NotImplementedError('Implement functionality first')

    @override
    def close_connection(self) -> None:
        if self.__type == 'yandex':
            self.__underlying_client.close()
        elif self.__type == 'google':
            raise NotImplementedError('Implement functionality first')
        else:
            raise NotImplementedError('Implement functionality first')

    @override
    def rename_book(self, old_name: str, new_name: str) -> None:
        if self.__type == 'yandex':
            with self.__underlying_client as client:
                pass
        elif self.__type == 'google':
            raise NotImplementedError('Implement functionality first')
        else:
            raise NotImplementedError('Implement functionality first')

    @override
    def remove_book(self, book_name: str) -> bool | None:
        if self.__type == 'yandex':
            with self.__underlying_client as client:
                pass
        elif self.__type == 'google':
            raise NotImplementedError('Implement functionality first')
        else:
            raise NotImplementedError('Implement functionality first')

    @override
    def download_book(self, book_name: str):
        if self.__type == 'yandex':
            with self.__underlying_client as client:
                pass
        elif self.__type == 'google':
            raise NotImplementedError('Implement functionality first')
        else:
            raise NotImplementedError('Implement functionality first')

    @override
    def add_new_book(self, file_to_add: str, book: Book_data) -> bool | None:
        if self.__type == 'yandex':
            with self.__underlying_client as client:
                pass
        elif self.__type == 'google':
            raise NotImplementedError('Implement functionality first')
        else:
            raise NotImplementedError('Implement functionality first')

    @override
    def list_all_books(self) -> list[str] | None:
        if self.__type == 'yandex':
            with self.__underlying_client as client:
                all_files: list[str] = list(client.listdir(self.home_path))
                return all_files

        elif self.__type == 'google':
            raise NotImplementedError('Implement functionality first')
        else:
            raise NotImplementedError('Implement functionality first')

    @override
    def exist(self, path) -> bool | None:
        if self.__type == 'yandex':
            with self.__underlying_client as client:
                return self.__underlying_client.exists(path)

        elif self.__type == 'google':
            raise NotImplementedError('Implement functionality first')
        else:
            raise NotImplementedError('Implement functionality first')

    @override
    def upload_book(self, local_path, client_path):
        pass


class Virtual_device(IDevice, IBookable):
    """
    Virtual device, responsible for Yandex or Google Cloud or etc.
    Need to create 1 virtual device for Yandex and 1 for Google Cloud.
    """

    __local_device_logger: BotLogger
    __translator: Translator
    __client: Client

    def __init__(self, logger, virtual_client, client_type, device_name: str):
        self.__client = Client(virtual_client, client_type, VIRTUAL_START_PATH)
        self.__local_device_logger = logger
        self.device_name = device_name

    @override
    def init_device(self, current_dir: str | Path) -> None:
        if not self.__client.check_client():
            self.__local_device_logger.log('Wrong token, cannot init virt device')
            self.__client.close_connection()
            self.is_initialized = False
        else:
            self.__local_device_logger.log('Device initialized')
            self.is_initialized = True

    @override
    def get_device_info(self) -> None:
        pass

    @override
    def rename_book(self, old_name: str, new_name: str) -> None:
        path_to_rename: str = self.get_home_dir_path() + '/' + old_name
        if self.__client.exist(old_name) and IBookable.is_book(new_name):
            self.__client.rename_book(path_to_rename, new_name)
        else:
            self.__local_device_logger.log(f'Book not exist with name {old_name} or new name is not a book')
            return

    @override
    def list_all_books(self):
        self.__client.list_all_books()

    @override
    def close_connection(self):
        """
        Delete device entities in case of error or finish
        :return: None
        """
        self.__client.close_connection()

    @override
    def remove_book(self, book_name: str):
        path_to_del: str = self.get_home_dir_path() + '/' + book_name
        if self.__client.exist(path_to_del):
            self.__client.remove_book(path_to_del)
        else:
            self.__local_device_logger.log(f'Book is not exist with name {book_name}')
            return

    @override
    def download_book(self, book_name: str):
        path_to_down: str = self.get_home_dir_path() + '/' + book_name
        if self.__client.exist(path_to_down):
            self.__client.download_book(f'{book_name}')
        else:
            self.__local_device_logger.log(f'Book not found with name - {book_name}')

    @override
    def add_new_book(self, file_to_add_name: str, book: Book_data):
        book_name: str = book.get_book_name()
        if IBookable.is_book(book_name):
            path_to_upload: str = self.get_home_dir_path() + '/' + book_name
            self.__client.upload_book(file_to_add_name, path_to_upload)

        else:
            self.__local_device_logger.log(f'Given file is not a book with name - {book_name}')
            return

    @override
    def start_device(self):
        try:
            pass

        except Exception as e:
            raise Exception(f'Start device functionality failed due to - {e}.')

    def __init_device_entities(self):
        try:
            self.__translator = Translator()
        except Exception as e:
            raise Exception(f'Device initialization failed due to {e}.')

    ###Static methods:

    @staticmethod
    def create_yandex_virt_device(logger: BotLogger) -> Virtual_device | None:
        """
        Factory method for creating Yandex based virtual device
        """
        try:
            return Virtual_device(logger=logger,
                                  virtual_client=yadisk.YaDisk(token=manual_code_receive()),
                                  client_type='yandex',
                                  device_name='Yandex disk')
        except Exception as e:
            print(f'Failed to init Yandex disk device - {e}')

    @staticmethod
    def create_google_virt_device(logger: BotLogger) -> Virtual_device | None:
        """
        Factory method for creating Google based virtual device
        """
        try:
            SCOPES = ['https://www.googleapis.com/auth/drive']
            SERVICE_ACCOUNT_FILE = TOKEN_GOOGLE

            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES
            )
            service = build('drive', 'v3', credentials=credentials)

            return Virtual_device(logger=logger,
                                  virtual_client=service,
                                  client_type='google',
                                  device_name='Google drive')
        except Exception as e:
            print(f'Failed to init Google disk device - {e}')
