import os
import signal
import sys
from pathlib import Path
from typing import Final

from core.entities.App_config import App_config
from core.entities.BootLoader import BootLoader
from core.entities.BotLogger import BotLogger
from core.entities.device.IDevice import IDevice
from core.entities.device.Physical_device import Physical_device
from core.entities.device.Virtual_device import Virtual_device
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
global_logger_ptr: Final[BotLogger] = app_config.get_logger()  # global logger instance
bootloader: Final[BootLoader] = BootLoader(logger=global_logger_ptr, app_config=app_config)

devices: list[IDevice | None] = list()
"""
All devices to use in app.
Accept None as a device in case of initializing error.
"""


# run_processes: list[LW_process] = list()
# """
# Encapsulated processes
# """


def get_mount_points() -> None:
    """
    Scan mount points of e-books (Physical devices)
    """
    physical_devices_search_path: str = app_config.get_device_search_path()
    try:
        global_logger_ptr.log('Physical devices init begin')
        users_media_path = list(os.listdir(Path(physical_devices_search_path)))
        if len(users_media_path) > 0:
            physical_devices_search_path += users_media_path[0]  # get first user devices, change if several

        user_devices: Final[list[str]] = os.listdir(physical_devices_search_path)

        if len(user_devices) >= 1:
            global_logger_ptr.log('Found devices:')
            for dev_num, device in enumerate(user_devices):
                devices.append(Physical_device(device, app_config))
                global_logger_ptr.log(f'{dev_num} device: {device}')
        global_logger_ptr.log('Physical devices init ended')
    except Exception as e:
        global_logger_ptr.log(f'An exception in initializing physical devices - {e}')


def init_virtual_devices() -> None:
    """
    Initialize virtual devices
    """
    if app_config.is_init_virtual():
        try:
            global_logger_ptr.log('Virtual devices init begin')
            devices.append(Virtual_device.create_yandex_virt_device(global_logger_ptr))
            # devices.append(Virtual_device.create_google_virt_device(global_logger))
            global_logger_ptr.log('Virtual devices init end')
        except Exception as e:
            global_logger_ptr.log(f'Failed to init virtual devices - {e}')


def gracefully_exit_devices() -> None:
    """
    Close connection on all used devices
    """
    if devices is not None:
        global_logger_ptr.log('Started exit for all devices')
        for num, device in enumerate(devices):
            global_logger_ptr.log(f'Device with num {num} and name "{device.get_device_name()}" ending work')
            device.close_connection()
        global_logger_ptr.log('Ended exit for all devices')
    global_logger_ptr.log(f'"{APP_NAME}" utility ending work, bye')


def signal_handler(sig, frame):
    """
    Handle sig int command
    :param sig: signal
    :param frame: function to execute in case of signal
    :return: None
    """
    print('\n')
    if devices is not None:
        global_logger_ptr.log('Started exit for all devices')
        for num, device in enumerate(devices):
            global_logger_ptr.log(f'Device with num {num} and name "{device.get_device_name()}" ending work')
            device.close_connection()
        global_logger_ptr.log('Ended exit for all devices')
    global_logger_ptr.log(f'"{APP_NAME}" utility ending work, bye')
    exit(0)


# run app
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)  # if program goes wrong

    global_logger_ptr.log(f'"{APP_NAME}" utility starting')
    get_mount_points()
    init_virtual_devices()

    devices = list(filter(lambda x: x is not None, devices))  # clear not inited devices

    if len(devices) > 0:  # all devices (physical and virtual) check
        try:
            for device in devices:
                # run_processes.append(LW_process('', device.init_device, Path('.')))
                device.init_device(Path('/home/kirill/PycharmProjects'))
            bootloader.run_app_browser()
        except Exception as e:
            global_logger_ptr.log(f'All functionality failed with exception - {e}, app exiting')

    else:
        global_logger_ptr.log('No connected devices to run app')

    gracefully_exit_devices()
    exit(0)
