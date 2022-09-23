import difflib
import time
import os
from datetime import datetime
from mirea_parser import MireaParser


class NewsParser(MireaParser):
    def __clear_images(self):
        if os.path.isdir('new_folder'):
            folder = 'images'
            for the_file in os.listdir(folder):
                file_path = os.path.join(folder, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(e)
                
    def __get_last_page_num(self) -> int:
        html = self._get_html(f'{self.mirea_url}/news')

        last_page_num = int(html.find(
            'div', {'class': ['bx-pagination-container', 'row']}).find_all('li', {'class': ''})[-1].text)

        # Парсим только первые 15 страниц, иначе парсинг очень долгий
        last_page_num = min(last_page_num, 15)

        return last_page_num

    def __get_news_details(self, url: str):
        html = self._get_html(url)

        news_block = html.find(
            'div', {'class': ['uk-grid-small', 'uk-grid', 'uk-grid-stack']})
        title = html.find('h1').text
        date = html.find('div', {'class': ["uk-margin-bottom"]}).text
        date_converted = datetime.strptime(date.strip(), "%d.%m.%Y").date()

        news_text = str(news_block.find(
            'div', {'class': ['news-item-text']}))

        tags_inline_block = news_block.find(
            'li', {'class': ['uk-display-inline-block']})

        if tags_inline_block is not None:
            tags = [tag.text for tag in tags_inline_block.find_all('a')]
        else:
            tags = []

        images = [self._get_image(self.mirea_url + image['href']) for image in news_block.find_all(
            'a', {'data-fancybox': 'gallery'}, href=True)]

        return title, date_converted, self._text_normalize(news_text), images, tags

    def __news_page_parse(self, url: str, is_ads_page: bool) -> bool:
        """Парсинг страницы с новостями и страниц с важными новостями."""
        html = self._get_html(url)

        news_bloc = html.find(
            'div', {'class': ['uk-grid-small', 'uk-grid', 'uk-grid-stack']})

        list_news = news_bloc.find_all(
            'div',
            class_='uk-width-1-3@m uk-width-1-4@l uk-margin-bottom'
            if is_ads_page
            else 'uk-width-1-2@m uk-width-1-3@l uk-margin-bottom',
        )


        is_important = is_ads_page
        for news in list_news:
            detail_page_url = news.find('a')['href']

            title, date, text, images, tags = self.__get_news_details(
                self.mirea_url + detail_page_url)

            latest_news = self._strapi.get_news(is_ads_page)

            if len(latest_news) > 0:
                list_matchers = [difflib.SequenceMatcher(
                    None, news['attributes']['text'].lower(), text.lower()) for news in latest_news]

                # если в списке есть новости с почти одинаковым содержимым, то парсинг
                # следует остановить
                stop = [match.ratio() for match in list_matchers]

                if True in stop:
                    return True

            response_images = []
            response_tags = []
            for image in images:
                response_image = self._strapi.upload(image, f'images/{image}')
                if response_image is not None:
                    response_images.append(response_image)

            for tag in tags:
                response_tag = self._strapi.add_tag(tag)
                response_tags.append(response_tag)

            self._strapi.create_news(
                title, text, is_important, response_tags, date.isoformat(), response_images)

            print(f'Successfully created \"{title}\"')

        return False

    def run(self) -> None:
        start = time.time()

        self.__clear_images()

        # парсинг первых 15 страниц новостей
        for i in range(1, self.__get_last_page_num() + 1):
            print(f'Pargsin news page {str(i)}')
            if self.__news_page_parse(
                f'{self.mirea_url}/news/?PAGEN_1={i}', False
            ):
                break

        # парсинг объявлений со страницы "Важное"
        print('Pargsin ads page')
        self.__news_page_parse(f'{self.mirea_url}/ads/', True)

        print(f"Done! The parser stopped after {time.time() - start}sec")
