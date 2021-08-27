from models import NewsModel
from typing import List, Optional
from request_setting import Request
from database import NewsDB, Image, Session, Tag, secondary_tag
import time
from main import config, os
from datetime import datetime
import os
import requests
from markdownify import markdownify as md


class News():
    def __init__(self, db: Session, http_session: requests.Session) -> None:
        self.start_url = config['project']['url']
        self.place_media = config['database']['media_folder']
        self.db = db
        self.http_session = http_session

        result = db.query(NewsDB).order_by(NewsDB.date.desc()).first()
        self.latest_news_item = result

    def __get_max_pages(self) -> int:
        html = Request.parse(self.start_url+'/news', self.http_session)

        max_page = int(html.find(
            'div', {'class': ['bx-pagination-container', 'row']}).find_all('li', {'class': ''})[-1].text)

        max_page = 15 if max_page > 15 else max_page

        return max_page

    def __add_to_database(self, news: NewsDB, images: Optional[List[Image]], tags: Optional[List[Image]]) -> None:
        self.db.add(news)
        news.images.extend(images)
        news.tags.extend(tags)
        self.db.commit()
        # session been close auto

    def __get_photo_name(self, url: str) -> str:
        """Получаем свойство фотографии после её скачивания"""

        # request
        file = Request.download_file(
            url, self.place_media+"/", self.http_session)

        return os.path.basename(file.name)

    def __news_detail_parse(self, url: str) -> None:
        """Парсинг детально одной новости"""
        html = Request.parse(url, self.http_session)

        news_block = html.find(
            'div', {'class': ['uk-grid-small', 'uk-grid', 'uk-grid-stack']})
        title = html.find('h1').text
        date = html.find('div', {'class': ["uk-margin-bottom"]}).text
        date_converted = datetime.strptime(date, " %d.%m.%Y").date()

        news_text = md(str(news_block.find(
            'div', {'class': ['news-item-text']})))

        tags = [tag.text for tag in news_block.find(
            'li', {'class': ['uk-display-inline-block']}).find_all('a')]

        images = [self.__get_photo_name(self.start_url+image['href']) for image in news_block.find_all(
            'a', {'data-fancybox': 'gallery'}, href=True)]

        print("SUCCESS Parse {}".format(title))

        return title, date_converted, news_text, [Image(name=name) for name in images], Tag.search(tags, self.db)

    def __news_page_parse(self, url) -> bool:
        """Парсинг страницы с новостями возвращает значение stop -
        True, если парсинг следует остановить и False, если продолжить
        """
        html = Request.parse(url, self.http_session)

        news_bloc = html.find(
            'div', {'class': ['uk-grid-small', 'uk-grid', 'uk-grid-stack']})

        # Получение новостей на странице /news=?PAGE=1 и ...
        list_news = news_bloc.find_all(
            'div', class_='uk-width-1-2@m uk-width-1-3@l uk-margin-bottom')

        # Парсим каждую найденую новость
        for news in list_news:
            detail_page_url = news.find('a')['href']
            title, date, text, images, tags = self.__news_detail_parse(
                self.start_url + detail_page_url)
            if self.latest_news_item is not None:
                stop = title == self.latest_news_item.title and date == self.latest_news_item.date
                if stop is False:
                    self.__add_to_database(
                        NewsDB(title=title, date=date, text=text), images, tags=tags)
                else:
                    return True
            else:
                self.__add_to_database(
                    NewsDB(title=title, date=date, text=text), images, tags=tags)

        return False

    def start_parsing(self) -> None:
        """Главный метод по запуску парсинга новостей"""
        start = time.time()
        for i in range(1, self.__get_max_pages() + 1):
            print('Pargsin page ' + str(i))
            if self.__news_page_parse(
                    '{}/news/?PAGEN_1={}'.format(self.start_url, i)):
                break

        print(
            "PARSING IS STOP, Time need : {} Sec".format(time.time() - start))
