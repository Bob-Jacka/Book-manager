import os

import pytest
from requests_oauthlib import OAuth2Session


@pytest.fixture(scope='session')
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark tests as slooow")


@pytest.fixture(scope="session")
def yandex_disk_session():
    client_id = os.environ["YANDEX_CLIENT_ID"]
    client_secret = os.environ["YANDEX_CLIENT_SECRET"]
    refresh_token = os.environ["YANDEX_REFRESH_TOKEN"]
    token_url = "https://oauth.yandex.ru/token"

    def token_saver(token):
        pass

    session = OAuth2Session(
        client_id,
        auto_refresh_url=token_url,
        auto_refresh_kwargs={
            "client_id": client_id,
            "client_secret": client_secret,
        },
        token=refresh_token,
        token_updater=token_saver,
    )
    return session
