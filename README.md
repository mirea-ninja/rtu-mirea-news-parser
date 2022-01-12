# rtu-mirea-news-parser
Парсинг новостей с официального сайта РТУ МИРЭА и сохранение их с помощью [REST Strapi](https://github.com/Ninja-Official/rtu-mirea-app-cms).

Проверка новостей происходит каждую минуту. Парсер ищет только новые новости, сравнивая текстовое содержимое.

## Зависимости
- Docker

## Установка и запуск
1. Клонируйте репозиторий.
2. Создайте файл переменных среды `.env`, пример - https://github.com/Ninja-Official/rtu-mirea-news-parser/blob/parser-strapi/.env.example. Если вам не нужен Sentry, просто не указывайте его.
3. `docker build -t mirea_news_parser .`
4. `docker run mirea_news_parser --env-file .\.env`
