import logging
import toml
import os

config = toml.load('config.toml')

logging.basicConfig(filename='logs.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

if __name__ == '__main__':

    # Создание папки с медиа
    if not os.path.exists(config['database']['media_folder']):
        os.mkdir(config['database']['media_folder'])
    from news_parse import News
    news = News()
    news.start_parsing()
