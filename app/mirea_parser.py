import os
import requests
import secrets
import re
from config import get_settings
from strapi import Strapi
from bs4 import BeautifulSoup as bs4
from abc import abstractmethod


class MireaParser():
    def __init__(self):
        self.mirea_url = 'https://mirea.ru/'
        self._requests_session = requests.Session()
        self._strapi = Strapi(get_settings().api_url, get_settings().api_token)

    def _text_normalize(self, text: str) -> str:
        return re.sub(r'^ ', '', text, flags=re.MULTILINE)

    def _download_image(self, url: str):
        """Скачать изображение в папку '/images'

        Args:
            url (str): прямая ссылка на изображение

        Returns:
            BufferedWriter: файл, открытый для записи
        """
        response = self._requests_session.get(url)
        if not os.path.exists('images'):
            os.makedirs('images')
        with open('images/' + secrets.token_hex(nbytes=16) + os.path.splitext(url)[1], 'wb') as file_image:
            file_image.write(response.content)
        return file_image

    def _get_html(self, url: str) -> bs4:
        """Получить BeautifulSoup объект для парсинга html страницы по URL

        Args:
            url (str): ссылка на страницу
        """
        response_text = self._requests_session.get(url).text
        html = bs4(response_text, 'lxml')
        return html

    def _get_image(self, url: str) -> str:
        image = self._download_image(url)

        return os.path.basename(image.name)

    @abstractmethod
    def run(self):
        pass
