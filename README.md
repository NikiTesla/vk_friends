**Django сервис друзей для стажировки в вк**

Сервис представляет из себя веб приложение в архитектурном стиле REST
_Ваши возможности как пользователя:_
    1. Зарегестировать аккаунт
    2. Отправить запрос дружбы другому пользователю
    3. Просматривать список входящих/исходящих запросов
    4. Отменять исходящие запросы, принимать и отклонять входящие
    5. Просматривать список друзей
    6. Удалять из друзей

_Для запуска сервиса у себя (вам понадобится docker и python):_
    1. Перейдите в папку, в которой планируете хранить исходный код проекта
    2. `git clone https://github.com/NikiTesla/vk_test.git`
    3. Если вы запускаете проект первый раз, сначала создайте контейнер для базы данных
        (спецификация описана в файле docker-compose.yml и контейнер создается при `make docker`)
    4. `make run` - программа для запуска проекта на устройстве в режиме debug
    5. `make docker` - создание образа с проектом и запуск его вместе с базой данной в docker
    6. Теперь сайт должен быть у вас на 127.0.0.1:8000
