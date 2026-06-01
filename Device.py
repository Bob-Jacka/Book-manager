import abc
import os
import sys

from core.entities.App_config import App_config
from core.entities.BootLoader import BootLoader
from core.entities.BotLogger import BotLogger
from core.entities.Translator import Translator
from core.other import LW_process
from data.Constants import (
    APP_NAME,
    STATIC_READ_FILE_NAME,
    STATIC_CONFIG_NAME
)


class Connect_device(abc.ABC):
    """
    Abstract class for support of connected devices.
    Implement Class for your device to use.
    """

    @abc.abstractmethod
    def connect(self):
        pass

    @abc.abstractmethod
    def get_path(self):
        pass

    @abc.abstractmethod
    def generate_tmp_dir(self):
        pass

    @abc.abstractmethod
    def close_connection(self):
        pass


class Device(Connect_device):
    __global_logger: BotLogger = None
    __translator: Translator = None

    __app_config: App_config

    __console_process: LW_process = None
    __browser_process: LW_process = None

    def __init_device(self) -> None:
        """
        Initialize some useful application variables.
        Contains in base class for strategies
        :return: None
        """
        try:
            current_dir = App_config.path_to_dir_with_app()
            print('Check for config file in files directory by default name')
            os_name = sys.platform

            config_path = current_dir + STATIC_CONFIG_NAME  # path to look for config
            if not os.path.exists(config_path):
                __app_config = App_config(os_name)
                self.__global_logger.log('Config file not found, using default values in configuration')
            else:
                __app_config = App_config(os_name)
                __app_config.init_config(current_dir + STATIC_CONFIG_NAME)

            self.__global_logger.log(f'device initialized in "{current_dir}" path in filesystem')
            self.__global_logger.log('Checking for file with read file by default name')
            if os.path.exists(current_dir + STATIC_READ_FILE_NAME):
                self.__global_logger.log('Read books file found')
            else:
                self.__global_logger.log('Read books file not found')
            self.__global_logger.log('App initialized in manual mode')
            if __app_config.get_current_dir_name() is None:
                self.__global_logger.log('Current directory cannot be None.')
                raise Exception('Current directory cannot be None, init failed')
        except Exception as e:
            self.__global_logger.log(f'Some exception occurred in init app - {e}')
            raise Exception('Init device failed')

    def __init_device_entities(self):
        try:
            self.__global_logger = BotLogger()
            self.__translator = Translator()
        except Exception as e:
            print(f'Error in initializing app entities - {e}')
            raise Exception(f'App initialization failed due to {e}')

    def __start_device(self):
        is_multi: bool = self.__app_config.is_multithreaded_app_mode()

        # Upper level error handling
        try:
            bootloader = BootLoader(logger=self.__global_logger, app_config=self.__app_config)
            # if false - run browser version without different process
            if is_multi:
                __browser_process = LW_process('browser', target=bootloader.run_app_browser)
                __browser_process.start_proc()
            else:
                bootloader.run_app_browser()

        except Exception as e:
            self.__global_logger.log(f'An exception occurred during device initialization - {e}')
            raise Exception(f'Start device functionality failed due to - {e}')

    def __clean_device_entities(self):
        """
        Delete app entities in case of error or finish
        :return: None
        """
        if self.__console_process is not None or self.__browser_process is not None:
            if self.__console_process.still_alive():
                self.__console_process.close_process()

            if self.__browser_process.still_alive():
                self.__browser_process.close_process()
            __global_logger = None
            __translator = None


# solo run device
if __name__ == '__main__':
    try:
        device = Device()  # create device to test on
        print(f'"{APP_NAME}" utility starting')
        device.__init_app_entities()
        device.__init_app()
        device.__start_app()
    except Exception as e:
        print(f'All functionality failed with exception - {e}, app exiting')
        device.__clean_app_entities()
    print(f'"{APP_NAME}" utility ending work, bye')
    exit(1)
