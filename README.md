![Build Status](https://github.com/Daelin148/foodgram/actions/workflows/main.yml/badge.svg)

# Foodgram

## Стек использованных технологий

___
[![Python 3](https://img.shields.io/badge/-Python-3670A0?style=for-the-badge&logo=Python&logoColor=ffdd54)](https://www.python.org/) [![Django](https://img.shields.io/badge/-Django-23092E20?style=for-the-badge&logo=Django&logoColor=white)](https://www.djangoproject.com/) [![Django REST framework](https://img.shields.io/badge/Django%20REST%20framework-ff1709?style=for-the-badge&logo=django&logoColor=white&color=00e5cc&labelColor=00e5cc)](https://www.django-rest-framework.org/) [![JWT + Djoser](https://img.shields.io/badge/-JWT%20%2B%20Djoser-black?style=for-the-badge&logo=JSON%20web%20tokens)](https://djoser.readthedocs.io/en/latest/introduction.html) [![Docker](https://img.shields.io/badge/-Docker-2496ed?style=for-the-badge&logo=Docker&logoColor=white)](https://www.docker.com/) [![React](https://img.shields.io/badge/-React-grey?style=for-the-badge&logo=React)](https://react.dev/) [![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-lightgrey?style=for-the-badge&logo=PostgreSQL)](https://www.postgresql.org/) [![Nginx](https://img.shields.io/badge/-Nginx-CD853F?style=for-the-badge&logo=Nginx&logoColor=white)](https://nginx.org/ru/) [![Gunicorn](https://img.shields.io/badge/-Gunicorn-298729?style=for-the-badge&logo=Gunicorn&logoColor=white)](https://gunicorn.org/#docs)
___

### Описание проекта

Проект «Фудграм» — сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Проект доступен по [адресу] (https://myfoodgramproject.zapto.org)

Для неавторизированных пользователей доступно:
- Зарегистрироваться / создать аккаунт.
- Просматривать рецепты на главной странице.
- Просматривать отдельные страницы рецептов.
- Просматривать страницы пользователей.
- Фильтровать рецепты по тегам.


Для авторизованных пользователей доступно:
- Авторизация в системе под своим логином и паролем.
- Выход из системы.
- Смена пароля.
- Создание/редактирование/удаление собственных рецептов.
- Просмотр рецепов на главной странице.
- Просмотр страниц пользователей.
- Просмотр отдельных страниц рецептов.
- Фильтровать рецепты по тегам.
- Работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов.
- Работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл с количеством необходимых ингредиентов для рецептов из списка покупок.
- Подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.


Администратор обладает всеми правами авторизованного пользователя. Плюсом он может:
- Изменять пароль любого пользователя.
- Создавать/блокировать/удалять аккаунты пользователей.
- Редактировать/удалять любые рецепты.
- Добавлять/удалять/редактировать ингредиенты.
- Добавлять/удалять/редактировать теги.

### Как развернуть проект на удаленном сервере

1. Форкнуть репозиторий в свой Github и клонировать  его:

```
git clone https://github.com/{Username}/foodgram
```
2. Добавить следующие secrets в settings своего репозитория:
- ALLOWED_HOSTS             # список хостов, которые могут отправить запрос на бэкенд
- DJANGO_SECRET_KEY         # значение переменной SECRET_KEY
- DOCKER_NAME               # никнейм в DockerHub
- DOCKER_PASSWORD           # пароль пользователя в DockerHub
- DOCKER_USERNAME           # имя пользователя в DockerHub
- HOST                      # ip_address удалённого сервера
- SETTINGS_DEBUG            # значение переменной SETTINGS True/False
- SSH_KEY                   # приватный ssh-ключ сервера
- SSH_PASSPHRASE            # кодовая фраза (пароль) для ssh-ключа
- TELEGRAM_TO               # id пользователя в Telegram
- TELEGRAM_TOKEN            # токен телеграм бота
- USER                      # логин на удалённом сервере

3. Создать Docker-образы
    ```
    cd foodgram
    cd frontend
    docker build -t username/foodgram-frontend .
    cd ../backend
    docker build -t username/foodgram-backend .
    ```
4. Загрузить образы на DockerHub
    ```
    bash
    docker push username/foodgram-frontend
    docker push username/foodgram-backend
    ```

5. Создать папку foodgram на вашем сервере и скопировать в нее:
- .env, добавив в него переменные из списка в файле .env.example в корне проекта
Создать папку infra в папке foodgram и скопировать в неё
- docker-compose.production.yml

6. Запустить docker compose в режиме демона:

    ```
    sudo docker compose -f docker-compose.production.yml up -d
    ```
7. Выполнить миграции, собрать статику бэкенда и скопировать их в /static/static/:

    ```
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_ingredients_csv
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
    sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static/
    ```

8. Изменить конфиг Ngix в зависимости от имеющегося. Например:

    ```
    sudo nano /etc/nginx/sites-enabled/default
    ```
    ```
    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:9000;
    }
    ```

9. Проверить конфиг Nginx и перезапустить его:

    ```bash
    sudo nginx -t
    sudo service nginx reload
    ```

### Настройка CI/CD

1. Файл workflow уже написан. Он находится в директории

    ```bash
    foodgram/.github/workflows/main.yml
    ```
2. После пуша в ветку main будут выполнены следующие джобы:
- проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8)
- билд и пуш контейнеров frontend и backend на DockerHub
- автоматический деплой проекта на боевой сервер
- при успешном деплое отправка сообщения в Telegram с информацие о коммите


### Автор проекта
[Daelin148] (https://github.com/Daelin148)