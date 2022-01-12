# rtu-mirea-news-parser
Парсинг новостей с официального сайта РТУ МИРЭА и сохранение их с помощью [REST Strapi](https://github.com/Ninja-Official/rtu-mirea-app-cms).
![image](https://user-images.githubusercontent.com/51058739/149154507-67825bbe-2e0e-499d-8618-3146d5c8cf3d.png)

Проверка новостей происходит каждую минуту. Парсер ищет только новые новости, сравнивая текстовое содержимое.

## Зависимости
- Docker

## Установка и запуск
1. Клонируйте репозиторий.
2. Переименуйте файл переменных среды `.env.example` в `.env` и укажите ваш API URL и сгенерированный токен, пример - https://github.com/Ninja-Official/rtu-mirea-news-parser/blob/parser-strapi/.env.example. Если вам не нужен Sentry, просто не указывайте его.
3. `docker build -t mirea_news_parser .`
4. `docker run mirea_news_parser --env-file .\.env`
