import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Final

from core.entities.BotLogger import BotLogger
from data.Constants import INPUT_SYM, STATIC_DIR_NAME_FOR_FAV, OSType


class Config_param_names(str, Enum):
    """
    Enum class with config names to proceed
    """
    READ_BOOK_FILE_NAME = 'read_book_file'
    AUTO_MODE = 'is_auto_mode'
    ENABLE_LOGS = 'is_enable_logs'
    EXCLUDE_DIRS = 'exclude_directories'
    CENTRAL_DIR = 'central_dir'
    VIRTUAL_DEVICES = 'is_virtual'


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


@dataclass
class App_config(metaclass=SingletonMeta):
    """
    Class for configuration application with parameters.
    Simple store variables app configuration.
    Also store and manage paths in utility.
    """

    __run_os: str
    """
    Which os (operating system) is using to run utility
    """

    __read_book_file: str
    """
    Default name of the file with read book.
    """

    __config_name: str
    """
    Default name of the config file
    """

    __is_enable_logs: bool
    """
    Is logs in application enabled.
    """

    __exclude_directories: list[str]
    """
    Which directories to ignore by app.
    Contains string objects.
    """

    __central_dir: str
    """
    directory address where app stored (home directory path)
    """

    __current_dir: str
    """
    pointer to current working directory of the application
    """

    __is_virtual: bool
    """
    Use virtual devices also
    """

    __global_logger: Final[BotLogger] = BotLogger()
    """
    Global instance of logger class.
    Logger creates in different branches of app execution.
    """

    def __init__(self, run_os: str, read_book_file_name: str = 'read.txt', config_file_name: str = 'config.txt',
                 is_auto: bool = True, is_logs: bool = False, is_virtual: bool = False, exclude_dirs: list = None):
        # Main config parameters:
        self.__run_os = run_os
        self.__central_dir = self.path_to_dir_with_app()  # get current directory #TODO change
        self.__current_dir = self.__central_dir

        # Other config parameters:
        self.__read_book_file = read_book_file_name
        self.__config_name = config_file_name
        self.__is_auto_mode = is_auto  # also used for interactive or not mode
        self.__is_enable_logs = is_logs  # turn off if you want to disable logs
        self.__is_virtual = is_virtual
        self.__exclude_directories = exclude_dirs

    def get_help_config(self) -> None:
        print('App config help.')
        print('Config can contain next parameters:')
        print('1. read_book_file_name - name of the file with read books,')
        print('2. is_auto_mode - turn on by default auto mode in application,')
        print('3. is_enable_logs - turn on of off logs in application,')
        print('4. exclude_directories - which directories to ignore by book search.')
        print('5. home directory - start directory of the app work.')
        print('How to write config file:')
        print('Write in config file next lines')

        print('read_book_file_name: <your file name>')
        print('is_auto_mode: <true or false values>')
        print('is_enable_logs: <true or false values>')
        print('exclude_directories: <one_dir_name, second_dir_name, third_dir_name> (list with dirs names)')
        if not os.path.exists(self.__config_name):
            print('Config is not exits')
            while True:
                print('Would you like to create test config file in this directory - yes (y) or no (n)?')
                user_input = input(INPUT_SYM)
                if user_input == 'yes' or user_input == 'y':
                    App_config.create_tmp_config()
                    break
                else:
                    break

    def path_to_read_file(self) -> str:
        return self.__central_dir + self.__read_book_file

    def init_config(self, config_file_path: str) -> None:
        """
        Initialize app by given config.
        Parse config file and get line by line parameters
        :param config_file_path: name of the config file to init.
        :return: None
        """
        with open(config_file_path) as file:
            for line in file:
                if ':' in line:
                    split_line = line.split(':')
                    value = split_line[1].strip()  # value for setting into configuration parameter
                    name = split_line[0].strip()
                    if value != '' and name != '':
                        if name == Config_param_names.READ_BOOK_FILE_NAME.value:
                            self.__read_book_file = value
                        elif name == Config_param_names.ENABLE_LOGS.value:
                            self.__is_enable_logs = bool(value)
                        elif name == Config_param_names.AUTO_MODE.value:
                            self.__is_auto_mode = bool(value)
                        elif name == Config_param_names.VIRTUAL_DEVICES:
                            self.__is_virtual = bool(value)
                        elif name == Config_param_names.EXCLUDE_DIRS.value:
                            if value == 'None':
                                self.__exclude_directories = list()
                        elif name == Config_param_names.CENTRAL_DIR.value:
                            if value == 'None':
                                self.__central_dir = ""
                        else:
                            raise Exception(f'Wrong config parameter - {line}')
                    else:
                        print(f'Value cannot be none in {line}')
                else:
                    raise Exception(f'Wrong config parameter split symbol - {line}')
            else:
                raise Exception('Exception in checking lines')

    def get_read_file_name(self) -> str:
        if self.__read_book_file is not None:
            return self.__read_book_file
        else:
            raise Exception('Try to get null value, failed')

    def get_config_file_name(self) -> str:
        if self.__config_name is not None:
            return self.__config_name
        else:
            raise Exception('Try to get null value')

    def get_is_auto_mode(self) -> bool:
        if self.__is_auto_mode is not None:
            return self.__is_auto_mode
        else:
            raise Exception('Try to get null value')

    def get_is_global_enable_log(self) -> bool:
        """
        Return bool value is global logs enabled
        :return:
        """
        if self.__is_enable_logs is not None:
            return self.__is_enable_logs
        else:
            raise Exception('Try to get null value')

    def get_exclude_dirs(self) -> list[str]:
        if self.__exclude_directories is not None:
            return self.__exclude_directories
        else:
            raise Exception('Try to get null value')

    def get_central_dir_name(self) -> str:
        if self.__central_dir is not None:
            return self.__central_dir
        else:
            raise Exception('Central directory path is None')

    def get_current_dir_name(self) -> str:
        if self.__current_dir is not None:
            return self.__current_dir
        else:
            raise Exception('Current directory is unknown')

    def is_init_virtual(self) -> bool:
        if self.__is_virtual is not None:
            return self.__is_virtual
        else:
            raise Exception('Multithread mode is None')

    def get_logger(self):
        return self.__global_logger

    @staticmethod
    def create_tmp_config(path: str | Path):
        """
        Creates config if you cannot do it by yourself.
        :return: None
        """
        try:
            with open(path + '/config.txt', 'w+') as tmp_config:
                tmp_config.write(f'{Config_param_names.READ_BOOK_FILE_NAME.value}: read.txt')
                tmp_config.write('\n')
                tmp_config.write(f'{Config_param_names.AUTO_MODE.value}: false')
                tmp_config.write('\n')

                tmp_config.write(f'{Config_param_names.ENABLE_LOGS.value}: false')
                tmp_config.write('\n')
                tmp_config.write(f'{Config_param_names.EXCLUDE_DIRS.value}: None')
                tmp_config.write('\n')
                tmp_config.write(f'{Config_param_names.CENTRAL_DIR.value}: None')
                tmp_config.write('\n')
            print('Config file created successfully with default parameters in it')
        except Exception as e:
            print(f'Exception in create config file - {e}, file not created')

    @staticmethod
    def path_to_dir_with_app(end_with: str = '') -> str:
        """
        Get real path to file with back system separator if you not provide end_with value.
        By default, return path to central directory (utility home);
        Example - if your app is stored in /home/user/books, than app archive will be pointing to /home/user/books
        :param end_with: value that will be inserted at back of the path
        :return: string value, representing path in your system
        """
        return Path(os.getcwd()).parent.absolute().as_posix() + os.sep + end_with

    def path_to_stored_books(self):
        return self.path_to_dir_with_app() + STATIC_DIR_NAME_FOR_FAV

    def get_device_search_path(self) -> str | None:
        if self.__run_os == OSType.linux_os:
            return '/run/media/'
        elif self.__run_os == OSType.windows_os:
            return ''
        return None

    def get_run_os(self) -> str:
        return self.__run_os


class App_config_builder:
    """
    Builder class for App_config.
    Provides step-by-step configuration of App_config instance.
    """

    def __init__(self):
        self._run_os: str = ""
        self._read_book_file_name: str = 'read.txt'
        self._config_file_name: str = 'config.txt'
        self._is_auto: bool = True
        self._is_logs: bool = False
        self._is_multithread: bool = False
        self._exclude_dirs: list = None

    def set_run_os(self, os_name: str) -> 'App_config_builder':
        self._run_os = os_name
        return self

    def set_read_book_file_name(self, name: str) -> 'App_config_builder':
        self._read_book_file_name = name
        return self

    def set_config_file_name(self, name: str) -> 'App_config_builder':
        self._config_file_name = name
        return self

    def set_auto_mode(self, is_auto: bool) -> 'App_config_builder':
        self._is_auto = is_auto
        return self

    def set_logs(self, is_logs: bool) -> 'App_config_builder':
        self._is_logs = is_logs
        return self

    def set_multithread(self, is_multithread: bool) -> 'App_config_builder':
        self._is_multithread = is_multithread
        return self

    def set_exclude_dirs(self, dirs: list) -> 'App_config_builder':
        self._exclude_dirs = dirs
        return self

    def build(self) -> 'App_config':
        return App_config(
            run_os=self._run_os,
            read_book_file_name=self._read_book_file_name,
            config_file_name=self._config_file_name,
            is_auto=self._is_auto,
            is_logs=self._is_logs,
            is_multithread=self._is_multithread,
            exclude_dirs=self._exclude_dirs
        )
