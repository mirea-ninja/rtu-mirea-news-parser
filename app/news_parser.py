import difflib
import logging
import os
import re
import time
from datetime import datetime
from typing import Any

import spacy
from mirea_parser import MireaParser

nlp = spacy.load("ru_core_news_md")

logger = logging.getLogger(__name__)


class NewsParser(MireaParser):
    def __clear_images(self):
        """Удаление всех изображений из папки images."""
        images_dir = "images"
        if not os.path.exists(images_dir):
            os.mkdir(images_dir)
            return

        for file in os.listdir(images_dir):
            os.remove(os.path.join(images_dir, file))

    def __get_last_page_num(self) -> int:
        html = self._get_html(f"{self.MIREA_URL}/news")

        last_page_num = int(
            html.find("div", {"class": ["bx-pagination-container", "row"]})
            .find_all("li", {"class": ""})[-1]
            .text
        )

        return min(last_page_num, 15)

    def __parse_news_details(
        self, url: str
    ) -> tuple[str, datetime.date, str, list[str], list[str] | list[Any]]:
        """Получение детальной информации о новости.
         Возвращает кортеж из:
        - заголовка
        - текста
        - даты
        - списка тегов
        - списка изображений
        """
        html = self._get_html(url)

        news_block = html.find(
            "div", {"class": ["uk-grid-small", "uk-grid", "uk-grid-stack"]}
        )
        title = html.find("h1").text
        date = html.find("div", {"class": ["uk-margin-bottom"]}).text
        date_converted = datetime.strptime(date.strip(), "%d.%m.%Y").date()

        news_text = str(news_block.find("div", {"class": ["news-item-text"]}))

        tags_inline_block = news_block.find(
            "li", {"class": ["uk-display-inline-block"]}
        )

        if tags_inline_block is not None:
            tags = [tag.text for tag in tags_inline_block.find_all("a")]
        else:
            tags = []

        images = [
            self._get_image(self.MIREA_URL + image["href"])
            for image in news_block.find_all(
                "a", {"data-fancybox": "gallery"}, href=True
            )
        ]

        return title, date_converted, self._text_normalize(news_text), images, tags

    def __parse_page(self, url: str, is_ads_page: bool) -> bool:
        """Парсинг страницы с новостями. Возвращает True, если на странице имеются новости, которые уже есть в базе.
        Это нужно для того, чтобы завершить парсинг на этой странице."""
        html = self._get_html(url)

        news_block = html.find(
            "div", {"class": ["uk-grid-small", "uk-grid", "uk-grid-stack"]}
        )

        news_in_page = news_block.find_all(
            "div",
            class_="uk-width-1-3@m uk-width-1-4@l uk-margin-bottom"
            if is_ads_page
            else "uk-width-1-2@m uk-width-1-3@l uk-margin-bottom",
        )

        is_important = is_ads_page

        # Последние сохраненные новости
        latest_news = self._strapi.get_news(is_ads_page)

        for news in news_in_page:
            detail_page_url = news.find("a")["href"]

            title, date, text, images, tags = self.__parse_news_details(
                self.MIREA_URL + detail_page_url
            )

            print("Latest news: ", latest_news)
            # Если новость уже есть в базе, то завершаем парсинг на этой странице
            if len(latest_news) > 0 and self.__is_news_exist(latest_news, title, text):
                return True

            response_images = []
            response_tags = []
            for image in images:
                response_image = self._strapi.upload(image, f"images/{image}")
                if response_image is not None:
                    response_images.append(response_image)

            for tag in tags:
                response_tag = self._strapi.add_tag(tag)
                response_tags.append(response_tag)

            self._strapi.create_news(
                title,
                text,
                is_important,
                response_tags,
                date.isoformat(),
                response_images,
            )

            logger.info(f"Добавлена новость: {title}")

        return False

    def __is_news_exist(self, latest_news: dict, title: str, text: str) -> bool:
        """Проверка, есть ли новость в списке последних сохраненных новостей."""
        if title.lower().replace(" ", "") in [
            news_item["attributes"]["title"].lower().replace(" ", "")
            for news_item in latest_news
        ]:
            logger.info("Новость уже есть в базе")
            logger.info("Новость: ", title)
            return True

        def remove_html_tags(text_with_tags: str) -> str:
            """Удаление html тегов из текста"""
            return re.sub("<[^<]+?>", "", text_with_tags)

        # Проверка на схожесть текста с помощью Spacy
        doc1 = nlp(remove_html_tags(text))
        doc2 = nlp(remove_html_tags(latest_news[0]["attributes"]["text"]))
        
        if doc1.similarity(doc2) > 0.92:
            logger.info("Новость уже есть в базе")
            logger.info("Новость: ", title)
            return True

        list_matchers = [
            difflib.SequenceMatcher(
                None,
                remove_html_tags(news["attributes"]["text"]).lower(),
                remove_html_tags(text).lower(),
            )
            for news in latest_news
        ]

        ratios = [matcher.ratio() for matcher in list_matchers]
        stop = any(ratio > 0.92 for ratio in ratios)

        return stop

    def run(self) -> None:
        start = time.time()

        self.__clear_images()

        # парсинг первых 15 страниц новостей
        for i in range(1, self.__get_last_page_num() + 1):
            logger.info(f"Парсинг страницы {i}")
            if self.__parse_page(f"{self.MIREA_URL}/news/?PAGEN_1={i}", False):
                break

        # парсинг объявлений со страницы "Важное"
        logger.info("Парсинг важных новостей")
        self.__parse_page(f"{self.MIREA_URL}/ads/", True)

        logger.info(f"Готово! Парсинг завершен за {time.time() - start} секунд")
