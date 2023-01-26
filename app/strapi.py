import requests


class Strapi:
    def __init__(self, api_url: str, api_token: str):
        self.api_url = api_url
        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {api_token}",
        }

    def get_news(self, is_important: bool, page_size: int = 50):
        """Получить список последних новостей, отсортированных по дате публикации (по убыванию)

        Params:
            is_important (bool): если True, то будут получены только важные новости
            page_size (int, optional): количество новостей на странице. По умолчанию 50.
        """
        request_url = (
            f"{self.api_url}/announcements?filters[isImportant][$eq]={str(is_important).lower()}&sort=date"
            f":DESC&pagination[pageSize]={page_size}"
        )
        response = requests.get(request_url, headers=self.headers).json()
        return [] if "error" in response else response["data"]

    def search_tag(self, tag: str) -> (int | None):
        """Получить id тега по названию

        Args:
            tag (str): название тега

        Returns:
            (int | None): id тега или None, если тег не найден
        """
        request_url = f"{self.api_url}/tags?filters[name][$eq]={tag}"
        response = requests.get(request_url, headers=self.headers).json()
        return response["data"][0]["id"] if "error" not in response else None

    def add_tag(self, tag: str):
        """Добавить новый тег

        Args:
            tag (str): название тега

        Returns:
            int: id нового тега или id тега с таким названием, если тег
            уже существует.
        """
        payload = {"data": {"name": tag}}
        response = requests.post(
            f"{self.api_url}/tags", headers=self.headers, json=payload
        ).json()

        if response["data"] is not None:
            return response["data"]["id"]

        return self.search_tag(tag)

    def create_news(
        self,
        title: str,
        text: str,
        is_important: bool,
        tags_id: list[int],
        date: str,
        images: list[int],
    ):
        """Создание новости

        Args:
            title (str): заголовок новости
            text (str): текст новости
            is_important (bool): если True, то новость будет помечена как "Важное"
            tags_id (list): список id тегов новости (List[int])
            date (str): дата новости в ISO формате
            images (list): список id изображений новости (List[int]), изображения
            должны быть загружены с помощью метода `upload`.
        """
        payload = {
            "data": {
                "isImportant": is_important,
                "title": title,
                "text": text,
                "date": date,
                "tags": tags_id,
            }
        }

        if images:
            payload["data"] |= {"images": [image["id"] for image in images]}

        requests.post(
            f"{self.api_url}/announcements", headers=self.headers, json=payload
        )

    def upload(self, file_name: str, file_path: str):
        files = {"files": (file_name, open(file_path, "rb"), "image", {"uri": ""})}
        response = requests.post(
            f"{self.api_url}/upload", headers=self.headers, files=files
        )

        # Игнорируем ошибки загрузки изображений, если файл слишком большой
        if response.status_code == 413:
            return None

        response = response.json()

        if len(response) > 0:
            if "id" in response[0]:
                return response[0]

        return None
