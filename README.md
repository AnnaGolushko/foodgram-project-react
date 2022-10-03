[![Foodgram](https://github.com/AnnaGolushko/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg?branch=master&event=push)](https://github.com/AnnaGolushko/foodgram-project-react/actions/workflows/foodgram_workflow.yml)

## Проект Foodgram (Продуктовый помощник)
Проект «Продуктовый помощник». На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

**[Анна Голушко](https://github.com/AnnaGolushko)**.

### Cписок используемых технологий:
- Django 
- Django-rest-framework
- Gunicorn
- PostgreSQL
- Nginx

### Как запустить проект:

1. Клонировать репозиторий 
2. Перейти в папку fodgram-project-react/infra/ и создать файл переменных окружения

```
cd fodgram-project-react/infra/
```
```
nano .env
```
Необходимо заполнить .env файл и задать значения для параметров:
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
SECRET_KEY=________ # ключ для проекта django
```
3. Запуск приложения в контейнерах Docker

Приложение подготовлено к запуску в контейнерах:
- db (контейнер базы данных)
- backend (контейнер API-приложения Django, WSGI-сервер gunicorn)
- nginx (контейнер веб-сервера. Получает запросы, перенаправляет в приложение, раздает статику)
- frontend (контейнер с SPA-приложением на React, штатно выключается самостоятельно)

Скрипт сборки контейнеров docker-compose.yml размещен в каталоге fodgram-project-react/infra/

Необходимо перейти в директорию fodgram-project-react/infra/ и выполнить команду

1 вариант - тихий запуск без логов
```
docker-compose up -d
```
2 вариант - после выполнения команды в консоль будут выводиться логи запуска контейнеров. 
Режим может использоваться для диагностики проблем запуска
```
sudo docker-compose up
```
После запуска контейнеров можно выполнить команду, чтобы проверить что все 3 контейнера запущены и работают:
```
sudo docker container ls
```
4. Миграции базы данных и первый вход в систему

Сразу после старта контейнеров необходимо выполнить следующие команды

4.1 Миграции
```
sudo docker-compose exec backend python manage.py makemigrations
sudo docker-compose exec backend python manage.py migrate
```
4.2 Создание суперпользователя для входа в административную панель
```
sudo docker-compose exec backend python manage.py createsuperuser
```
4.3 Сбор статических файлов
```
sudo docker-compose exec backend python manage.py collectstatic --no-input 
```

После этого приложение готово к работе.

### Загрузка тестовых данных
При желании вы можете загрузить тестовые данные, которые заранее подготовлены.

Загрузить ингредиенты в БД:
```
python manage.py load_ingredients_data
```

### Первый вход в систему
После запуска проект будет доступен по URL:
- http://127.0.0.1/api/docs/ - докуменация для API
- http://127.0.0.1/api/ - непосредственно API-интерфейс
- http://127.0.0.1/admin/ - административная панель


### Взаимодействие с API
Все доступные эндпоинты, правила обращения к ним и сведения о правах доступа описаны в документации проекта.