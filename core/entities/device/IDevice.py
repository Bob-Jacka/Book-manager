"""
File with important Device interfaces
"""

import abc
import os
import re
from pathlib import Path

from core.entities.Book_data import Book_data
from data.Constants import NON_BOOK_EXTENSIONS


class IBookable(abc.ABC):
    """
    Interface for book actions
    """

    # book specific methods:

    @abc.abstractmethod
    def rename_book(self, old_name: str, new_name: str) -> None:
        pass

    @abc.abstractmethod
    def remove_book(self, book_name: str) -> bool | None:
        """
        Remove book from device's storage
        """
        pass

    @abc.abstractmethod
    def download_book(self, book_name: str) -> None:
        """
        Download book from storage into host
        """
        pass

    @abc.abstractmethod
    def add_new_book(self, file_to_add: str, book: Book_data) -> bool | None:
        """
        Add new book into device's storage
        """
        pass

    @abc.abstractmethod
    def list_all_books(self) -> list[str]:
        """
        List all books that stored in device
        """
        pass

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


class IDevice(abc.ABC):
    """
    Abstract class for support of connected devices.
    Implement Class for your device to use.
    """

    is_initialized: bool = False
    device_name: str = ''
    start_path: str

    # device specific methods:
    @abc.abstractmethod
    def init_device(self, current_dir: str | Path) -> None:
        pass

    @abc.abstractmethod
    def close_connection(self) -> None:
        """
        Close device connection
        """
        pass

    @abc.abstractmethod
    def start_device(self) -> None:
        """
        Start device and all of it actions
        """
        pass

    def get_home_dir_path(self) -> str | None:
        """
        Get path where device is suited
        """
        return self.start_path

    @abc.abstractmethod
    def get_device_info(self) -> None:
        """
        Print device info into console
        """
        pass

    def get_device_name(self):
        return self.device_name

    def get_start_path(self):
        """
        Get start for device (I.e home directory where to start working)
        """
        return self.start_path

    def is_initialized_device(self) -> bool:
        """
        Simple getter for initialized state
        """
        return self.is_initialized


class IClient(abc.ABC):
    """
    Interface for clients in virtual devices
    """

    home_path: str
    """
    Central directory of the client
    """

    @abc.abstractmethod
    def init_connection(self) -> None:
        pass

    @abc.abstractmethod
    def close_connection(self) -> None:
        pass

    @abc.abstractmethod
    def check_path(self, path_to_check: str) -> bool | None:
        """
        Check path for validity in virtual device
        """
        pass

    @abc.abstractmethod
    def check_client(self) -> bool | None:
        """
        Check client
        """
        pass

    @abc.abstractmethod
    def exist(self, path) -> bool | None:
        """
        Check if path exist
        """
        pass

    @abc.abstractmethod
    def upload_book(self) -> None:
        """
        Upload book to virtual device
        """
        pass
