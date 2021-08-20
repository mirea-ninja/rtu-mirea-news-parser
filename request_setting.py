from bs4 import BeautifulSoup as BS
import secrets
import os
from typing import Optional
import requests


class Request():
    def parse(url: str, session: Optional[requests.Session] = requests):
        response = session.get(url)
        return BS(response.text, 'lxml')

    def post(url: str, data, headers=None, session: Optional[requests.Session] = requests):
        return session.post(url, data=data, headers=headers)

    # place - папка для хранения media
    def download_file(url: str, place, session: Optional[requests.Session] = requests):
        response = session.get(url)
        with open(place+secrets.token_hex(nbytes=16)+os.path.splitext(url)[1], 'wb') as file:
            file.write(response.content)
        return file

    def start_session():
        session = requests.Session()
        try:
            yield session
        finally:
            session.close()
