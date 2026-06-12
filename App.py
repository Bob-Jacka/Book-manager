import sys
from typing import Final

from Device import *
from core.entities.App_config import App_config
from core.entities.BootLoader import BootLoader
from core.entities.BotLogger import BotLogger
from data.Constants import APP_NAME, STATIC_CONFIG_NAME

os_name: Final[str] = sys.platform
app_config: App_config  # init config with current operational system

if not os.path.exists(App_config.path_to_dir_with_app(STATIC_CONFIG_NAME)):
    print('Config file not found, using default values in configuration')
    app_config = App_config(os_name)
else:
    app_config = App_config(os_name)
    app_config.init_config(App_config.path_to_dir_with_app(STATIC_CONFIG_NAME))

# global entities:
global_logger: Final[BotLogger] = app_config.get_logger()  # global logger instance
bootloader: Final[BootLoader] = BootLoader(logger=global_logger, app_config=app_config)
physical_devices_search_path: str = app_config.get_device_search_path()

devices: Final[list[IDevice]] = list()
"""
All devices to use in app
"""


def get_mount_points() -> None:
    """
    Scan mount points of e-books (Physical devices)
    """
    global physical_devices_search_path
    global_logger.log('Physical devices init begin')
    try:
        users_media_path = list(os.listdir(Path(physical_devices_search_path)))  # TODO change last catalogue
        if len(users_media_path) > 0:
            physical_devices_search_path += users_media_path[0]  # get first user devices, change if several

        user_devices: list = os.listdir(physical_devices_search_path)

        if len(user_devices) >= 1:
            global_logger.log('Found devices:')
            for dev_num, device in enumerate(user_devices):
                devices.append(Physical_device(device, app_config))
                global_logger.log(f'{dev_num} user: {device}')

    except Exception as e:
        global_logger.log(f'An exception in initializing physical devices - {e}')


async def init_virtual_devices() -> None:
    """
    Initialize virtual devices
    """
    if app_config.is_init_virtual():
        global_logger.log('Virtual devices init begin')
        try:
            devices.append(Virtual_device.create_yandex_virt_device(global_logger))
            devices.append(Virtual_device.create_google_virt_device(global_logger))
        except Exception as e:
            global_logger.log(f'Failed to init virtual devices - {e}')


# run app
if __name__ == '__main__':
    global_logger.log(f'"{APP_NAME}" utility starting')
    get_mount_points()
    if app_config.is_init_virtual():
        init_virtual_devices()
    if len(devices) > 0:  # all devices (physical and virtual) check
        try:
            # TODO Init devices
            bootloader.run_app_browser()
        except Exception as e:
            global_logger.log(f'All functionality failed with exception - {e}, app exiting')

    else:
        global_logger.log('No connected devices to run app')
    global_logger.log(f'"{APP_NAME}" utility ending work, bye')
    exit(1)
