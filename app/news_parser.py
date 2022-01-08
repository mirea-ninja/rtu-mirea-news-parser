import os
import requests
import difflib
import secrets
import time
import re
from config import get_settings
from strapi import Strapi
from bs4 import BeautifulSoup as bs4
from datetime import datetime
from markdownify import markdownify as md


class NewsParser():
    def __init__(self):
        self.mirea_url = 'https://mirea.ru/'
        self.requests_session = requests.Session()
        self.strapi = Strapi(get_settings().api_url, get_settings().api_token)

    def __text_normalize(self, text: str) -> str:
        return re.sub(r'^ ', '', text, flags=re.MULTILINE)

    def __download_image(self, url: str):
        response = self.requests_session.get(url)
        if not os.path.exists('images'):
            os.makedirs('images')
        with open('images/' + secrets.token_hex(nbytes=16) + os.path.splitext(url)[1], 'wb') as file_image:
            file_image.write(response.content)
        return file_image

    def __get_html(self, url: str) -> bs4:
        response_text = self.requests_session.get(url).text
        html = bs4(response_text, 'lxml')
        return html

    def __get_last_page_num(self) -> int:
        html = self.__get_html(self.mirea_url + '/news')

        last_page_num = int(html.find(
            'div', {'class': ['bx-pagination-container', 'row']}).find_all('li', {'class': ''})[-1].text)

        # Парсим только первые 15 страниц, иначе парсинг очень долгий
        last_page_num = 15 if last_page_num > 15 else last_page_num

        return last_page_num

    def __get_image(self, url: str) -> str:
        image = self.__download_image(url)

        return os.path.basename(image.name)

    def __get_news_details(self, url: str):
        html = self.__get_html(url)

        news_block = html.find(
            'div', {'class': ['uk-grid-small', 'uk-grid', 'uk-grid-stack']})
        title = html.find('h1').text
        date = html.find('div', {'class': ["uk-margin-bottom"]}).text
        date_converted = datetime.strptime(date.strip(), "%d.%m.%Y").date()

        news_text = str(news_block.find(
            'div', {'class': ['news-item-text']}))

        tags = [tag.text for tag in news_block.find(
            'li', {'class': ['uk-display-inline-block']}).find_all('a')]

        images = [self.__get_image(self.mirea_url + image['href']) for image in news_block.find_all(
            'a', {'data-fancybox': 'gallery'}, href=True)]

        print("SUCCESS Parse {}".format(title))

        return title, date_converted, self.__text_normalize(news_text), images, tags

    def __news_page_parse(self, url) -> bool:
        """Парсинг страницы с новостями. stop -
        bool массив, в котором ведётся поиск одинаковых новостей, 
        если парсинг следует остановить возвращаем True."""
        html = self.__get_html(url)

        news_bloc = html.find(
            'div', {'class': ['uk-grid-small', 'uk-grid', 'uk-grid-stack']})

        # Получение новостей на странице /news=?PAGE=1 и ...
        list_news = news_bloc.find_all(
            'div', class_='uk-width-1-2@m uk-width-1-3@l uk-margin-bottom')

        # Парсим каждую найденую новость
        for news in list_news:
            detail_page_url = news.find('a')['href']

            title, date, text, images, tags = self.__get_news_details(
                self.mirea_url + detail_page_url)

            latest_news = self.strapi.get_news()

            if len(latest_news) > 0:
                list_matchers = [difflib.SequenceMatcher(
                    None, news['attributes']['text'], text.lower()) for news in latest_news]

                stop = [match.ratio() > 0.91 for match in list_matchers]

                if True in stop:
                    return True

            response_images = []
            response_tags = []
            for image in images:
                response_image = self.strapi.upload(image, 'images/' + image)
                if response_image is not None:
                    response_images.append(response_image)
                    
            for tag in tags:
                response_tag = self.strapi.add_tag(tag)
                response_tags.append(response_tag)
            
            self.strapi.create_news(title, text, False, response_tags, date.isoformat(), response_images)

        return False

    def run(self) -> None:
        start = time.time()
        for i in range(1, self.__get_last_page_num() + 1):
            print('Pargsin page ' + str(i))
            if self.__news_page_parse(
                    '{}/news/?PAGEN_1={}'.format(self.mirea_url, i)):
                break

        print(
            "Done! The parser stopped after {}sec".format(time.time() - start))
