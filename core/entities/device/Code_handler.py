"""
Code handler for Yandex disk virtual device
"""

import http.server
import socketserver
from threading import Thread
from urllib.parse import urlparse, parse_qs

from requests_oauthlib import OAuth2Session

try:
    from data.Tokens import TOKEN_YANDEX, TOKEN_GOOGLE, TOKEN_YANDEX_SECRET, REFRESH_YANDEX_TOKEN
except FileNotFoundError:
    raise Exception('Create Tokens file in data directory and provide tokens')

auth_code = None


class CodeHandler(http.server.BaseHTTPRequestHandler):
    """
    Small http server for receiving access token
    """

    def do_GET(self):
        global auth_code
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        auth_code = query.get("code", [None])[0]

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()


def run_server():
    with socketserver.TCPServer(("localhost", 8080), CodeHandler) as httpd:
        httpd.handle_request()


def auto_token_receive():
    """
    Auto method for receiving yandex authorization code
    """
    client_id = TOKEN_YANDEX
    client_secret = TOKEN_YANDEX_SECRET
    redirect_uri = "https://oauth.yandex.ru/verification_code"
    auth_url = "https://oauth.yandex.ru/authorize"
    token_url = "https://oauth.yandex.ru/token"
    scope = ["cloud_api:disk.read", "cloud_api:disk.write", 'cloud_api:disk.app_folder', 'cloud_api:disk.info']

    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()

    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
    authorization_url, state = oauth.authorization_url(auth_url)

    print(f"Open in browser: {authorization_url}")

    while auth_code is None:
        pass

    token = oauth.fetch_token(
        token_url,
        code=auth_code,
        client_secret=client_secret
    )

    return token["access_token"]


def manual_code_receive():
    """
    Manual method of receiving yandex authorization code
    """
    global REFRESH_YANDEX_TOKEN
    client_id = TOKEN_YANDEX
    client_secret = TOKEN_YANDEX_SECRET
    redirect_uri = "https://oauth.yandex.ru/verification_code"
    auth_url = "https://oauth.yandex.ru/authorize"
    token_url = "https://oauth.yandex.ru/token"
    scope = ["cloud_api:disk.read", "cloud_api:disk.write", 'cloud_api:disk.app_folder', 'cloud_api:disk.info']

    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)

    authorization_url, state = oauth.authorization_url(auth_url)
    print(f"Authorize on site: {authorization_url}")

    print('Enter authorization token')
    code = input('>> ')

    token = oauth.fetch_token(
        token_url,
        code=code,
        refresh_token=REFRESH_YANDEX_TOKEN if REFRESH_YANDEX_TOKEN is not None else '',
        client_secret=client_secret,
        include_client_id=True
    )

    access_token = token["access_token"]
    REFRESH_YANDEX_TOKEN = token['refresh_token']
    print("Token received")
    return access_token
