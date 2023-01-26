import os
import re
import secrets
from abc import abstractmethod

import requests
from bs4 import BeautifulSoup as bs4
from strapi import Strapi


class MireaParser:
    MIREA_URL = "https://mirea.ru"

    def __init__(self, api_url: str, api_token: str):
        self._requests_session = requests.Session()
        self._strapi = Strapi(api_url, api_token)

    def _text_normalize(self, text: str) -> str:
        text = text.strip()
        text = re.sub(r"^ ", "", text, flags=re.MULTILINE)

        text = re.sub(r"<div.*?>", "", text, flags=re.MULTILINE)
        text = re.sub(r"</div>", "", text, flags=re.MULTILINE)

        return text

    def _download_image(self, url: str):
        """Скачать изображение в папку '/images'

        Args:
            url (str): прямая ссылка на изображение

        Returns:
            BufferedWriter: файл, открытый для записи
        """
        response = self._requests_session.get(url)
        if not os.path.exists("images"):
            os.makedirs("images")
        with open(
            f"images/{secrets.token_hex(nbytes=16)}{os.path.splitext(url)[1]}", "wb"
        ) as file_image:
            file_image.write(response.content)
        return file_image

    def _get_html(self, url: str) -> bs4:
        """Получить BeautifulSoup объект для парсинга html страницы по URL

        Args:
            url (str): ссылка на страницу
        """
        response_text = self._requests_session.get(url).text
        return bs4(response_text, "lxml")

    def _get_image(self, url: str) -> str:
        image = self._download_image(url)

        return os.path.basename(image.name)

    @abstractmethod
    def run(self):
        pass
