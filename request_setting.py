import requests as req
from bs4 import BeautifulSoup as BS
import secrets
import os


class Request():

    @staticmethod
    def parse(url):
        request = req.get(url)
        return BS(request.text, 'lxml')

    @staticmethod
    def post(url, data, headers=None):
        return req.post(url, data=data, headers=headers)

    # place - папка для хранения media
    @staticmethod
    def download_file(url, place):
        request = req.get(url)
        with open(place+secrets.token_hex(nbytes=16)+os.path.splitext(url)[1], 'wb') as file:
            file.write(request.content)
        return file
