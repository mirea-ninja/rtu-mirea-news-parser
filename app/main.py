import schedule
import time
from news_parser import NewsParser
from strapi import Strapi


def parse():
    parser = NewsParser()
    parser.run()


if __name__ == '__main__':
    schedule.every(1).minutes.do(parse)

    while True:
        schedule.run_pending()
        time.sleep(1)
