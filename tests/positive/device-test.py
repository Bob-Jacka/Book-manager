import pytest

from core.entities.BotLogger import BotLogger
from core.entities.device.Virtual_device import Virtual_device


@pytest.mark.slow
def test_create_physical_device():
    pass


@pytest.mark.slow
def test_create_virtual_device_yandex():
    device = Virtual_device.create_yandex_virt_device(BotLogger())
    assert device is not None


@pytest.mark.slow
def test_create_virtual_device_yandex():
    device = Virtual_device.create_google_virt_device(BotLogger())
    assert device is not None


@pytest.mark.slow
def test_get_files_from_virt_device():
    pass


@pytest.mark.slow
def test_init_devices():
    pass
