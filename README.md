# rtu-mirea-news-api
Данный сервис предназначен для парсинга новостей с сайта mirea.ru и получение их с помощью RestAPI. У новостей сохраняются все картинки и теги, а также html контент новостей преобразуется в Markdown формат, чтобы сохранить ссылочную информацию и т.п.

Обновление новостей в локальном хранилище происходит каждые 10 минут. Парсер ищет только новые новости, которых ещё нет в базе. Если таких нет, то он не продолжает работу.

## Зависимости
- Docker

## Как запустить
1. Клонируйте репозиторий.
2. Установите ваш хост в config.toml. Это нужно для получения изображений. https://github.com/Ninja-Official/rtu-mirea-news-api/blob/313a0b940f4f1857eae8abd1a08ae52689c5e676/config.toml#L7
3. Установите секретный API_KEY в https://github.com/Ninja-Official/rtu-mirea-news-api/blob/313a0b940f4f1857eae8abd1a08ae52689c5e676/docker-compose.yml#L9 и в refresh_invoker https://github.com/Ninja-Official/rtu-mirea-news-api/blob/313a0b940f4f1857eae8abd1a08ae52689c5e676/refresh_invoker/crontab#L1
4. `docker-compose build`
5. `docker-compose up`
