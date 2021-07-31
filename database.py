"""Работа со Strapi"""

from request_setting import Request
from app import config, logging


class DB():

    @staticmethod
    def add(data):
        url = config['database']['host']+':' + \
            config['database']['port']+config['database']['news_route']
        headers = {'Authorization': 'Bearer ' +
                   config['database']['strapi_jwt_token']}
        Request.post(url, data, headers)
        logging.info("SUCCESS add to database")
