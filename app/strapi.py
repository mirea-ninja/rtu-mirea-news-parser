import requests
from config import Settings


class Strapi:
    def __init__(self, api_url: str, api_token: str):
        self.api_url = api_url
        self.headers = {'accept': 'application/json',
                        'Authorization': 'Bearer ' + api_token}

    def get_news(self):
        response = requests.get(
            self.api_url + 'announcements', headers=self.headers).json()
        if 'error' in response:
            return []
        return response['data']

    def search_tag(self, tag: str):
        request_url = self.api_url + 'tags?filters[name][$eq]=' + tag
        response = requests.get(request_url, headers=self.headers).json()
        if 'error' not in response:
            return response['data'][0]['id']
        return None

    def add_tag(self, tag: str):
        payload = {'data': {'name': tag}}
        response = requests.post(
            self.api_url + 'tags', headers=self.headers, json=payload).json()

        if response['data'] is not None:
            return response['data']['id']

        return self.search_tag(tag)

    def create_news(self, title: str, text: str, is_important: bool, tags_id: list, date: str, images: list):
        payload = {'data': {'isImportant': is_important, 'title': title,
                       'text': text, 'date': date, 'tags': tags_id}}
        if len(images) != 0:
            payload.update({'images': [image['id'] for image in images]})
            print(payload)

        requests.post(self.api_url + 'announcements',
                    headers=self.headers, json=payload)

    def upload(self, file_name: str, file_path: str):
        files = {'files': (file_name, open(
            file_path, 'rb'), 'image', {'uri': ''})}
        response = requests.post(
            self.api_url + 'upload', headers=self.headers, files=files).json()

        if len(response) > 0:
            if 'id' in response[0]:
                return response[0]
        return None
