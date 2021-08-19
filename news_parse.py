from typing import List, Optional
from request_setting import Request
from database import NewsDB, Image, Session, Tag
import time
from main import config, logging, os
from datetime import datetime, date
import os
import requests


class News():
    def __init__(self, db: Session, http_session: requests.Session) -> None:
        self.start_url = config['project']['url']
        self.place_media = config['database']['media_folder']
        self.db = db
        self.http_session = http_session

    def get_max_pages(self) -> int:

        # request
        html = Request.parse(self.start_url+'/news', self.http_session)

        max_page = int(html.find(
            'div', {'class': ['bx-pagination-container', 'row']}).find_all('li', {'class': ''})[-1].text)
        return max_page

    def add_to_database(self, news: NewsDB, images: Optional[List[Image]], tags: Optional[List[Image]]) -> None:
        self.db.add(news)
        news.images.extend(images)
        news.tags.extend(tags)
        self.db.commit()
        # session been close auto

    def get_photo_name(self, url: str) -> str:
        """Получаем свойство фотографии после её скачивания"""

        # request
        file = Request.download_file(
            url, self.place_media+"/", self.http_session)

        return os.path.basename(file.name)

    def news_detail_parse(self, url: str) -> None:
        """Парсинг детально одной новости"""

        # request
        html = Request.parse(url, self.http_session)

        news_block = html.find(
            'div', {'class': ['uk-grid-small', 'uk-grid', 'uk-grid-stack']})
        title = html.find('h1').text
        date = html.find('div', {'class': ["uk-margin-bottom"]}).text
        date_convert = datetime.strptime(date, " %d.%m.%Y").date()
        news_text = news_block.find(
            'div', {'class': ['news-item-text']}).text
        tags = [tag.text for tag in news_block.find(
            'li', {'class': ['uk-display-inline-block']}).find_all('a')]
        images = [self.get_photo_name(self.start_url+image['href']) for image in news_block.find_all(
            'a', {'data-fancybox': 'gallery'}, href=True)]
        # add to database
        self.add_to_database(NewsDB(title=title, date=date_convert, text=news_text), [
                             Image(name=name) for name in images], tags=Tag.Search(tags, self.db))

        logging.info("SUCCESS Parse {}".format(title))

    def news_page_parse(self, url) -> None:
        """Парсинг страницы с новостями"""

        # request
        html = Request.parse(url, self.http_session)

        news_bloc = html.find(
            'div', {'class': ['uk-grid-small', 'uk-grid', 'uk-grid-stack']})

        # Получение новостей на странице /news=?PAGE=1 и ...
        list_news = news_bloc.find_all(
            'div', class_='uk-width-1-2@m uk-width-1-3@l uk-margin-bottom')

        # Парсим каждую найденую новость
        for news in list_news:
            detail_page_url = news.find('a')['href']
            self.news_detail_parse(self.start_url + detail_page_url)

    def start_parsing(self) -> None:
        """Главный метод по запуску парсинга новостей"""
        start = time.time()
        for i in range(1, self.get_max_pages()+1):
            self.news_page_parse(
                '{}/news/?PAGEN_1={}'.format(self.start_url, i))

        logging.info(
            "PARSING IS STOP, Time need : {} Sec".format(time.time() - start))
