from request_setting import Request
from database import DB
import time
from app import config, logging
from datetime import datetime, date


class News():

    def __init__(self) -> None:
        self.start_url = config['project']['url']
        html = Request.parse(self.start_url+'/news')
        self.place_media = config['database']['media_folder']
        self.max_page = int(html.find(
            'div', {'class': ['bx-pagination-container', 'row']}).find_all('li', {'class': ''})[-1].text)

    def get_photo_property(self, url):
        """Получаем свойство фотографии после её скачивания"""

        file = Request.download_file(url, self.place_media+"/")

    def news_detail_parse(self, url):
        """Парсинг страницы новости"""

        html = Request.parse(url)
        news_block = html.find(
            'div', {'class': ['uk-grid-small', 'uk-grid', 'uk-grid-stack']})
        title = html.find('h1').text
        date = html.find('div', {'class': ["uk-margin-bottom"]}).text
        date_convert = datetime.strptime(date, " %d.%m.%Y").date()
        news_text = news_block.find(
            'div', {'class': ['news-item-text']}).text
        images = [self.get_photo_property(self.start_url+image['href']) for image in news_block.find_all(
            'a', {'data-fancybox': 'gallery'}, href=True)]

        # Работает, но не обрабатывается images на стороне strapi!!!
        # DB.add({'title': title, 'date': str(date_convert),
        #        'text': news_text, 'images': ['a']})

        logging.info("SUCCESS Parse {}".format(title))

    def news_page_parse(self, url):
        """Парсинг страници с новостями"""

        html = Request.parse(url)
        news_bloc = html.find(
            'div', {'class': ['uk-grid-small', 'uk-grid', 'uk-grid-stack']})

        # Получение новостей на странице /news=?PAGE=1 и ...
        list_news = news_bloc.find_all(
            'div', class_='uk-width-1-2@m uk-width-1-3@l uk-margin-bottom')

        # Парсим каждую найденую новость
        for news in list_news:
            detail_page_url = news.find('a')['href']
            self.news_detail_parse(self.start_url + detail_page_url)

    def start_parsing(self):
        """Главный метод по запоску парсинга новостей"""

        start = time.time()
        for i in range(1, self.max_page+1):
            self.news_page_parse(
                '{}/news/?PAGEN_1={}'.format(self.start_url, i))
        logging.info(
            "PARSING IS STOP, Time need : {} Sec".format(time.time() - start))
