# homework_bot - отслеживание статуса код-ревью.
Бот работающий с API Яндекс.Практикум, а именно, отображает статус проверки кода работы.
Запросы отправляются каждые 10 минут на эндпоинт https://practicum.yandex.ru/api/user_api/homework_statuses/
Возможные ответы бота:
- Работа проверена: ревьюеру всё понравилось. Ура!  
- Работа взята на проверку ревьюером.  
- Работа проверена: у ревьюера есть замечания.

### Технологии:
* Python 3.9
* python-dotenv версии 0.19.0
* python-telegram-bot версии 13.7

### Запуск проекта в dev-режиме
- клонируйте репозиторий и перейдите в него в командной строке
```
git clone ссылка
cd api_final_yatube
```
- Разверните виртуальное окружение
```
python -m venv venv
```
- Активируйте виртуальное окружение
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 
- Выполните миграции
```
python3 manage.py migrate
```
- В папке с файлом manage.py выполните команду запуска dev-сервера:
```
python3 manage.py runserver
```
- Для остановки  dev-сервера нажми Ctrl+C или Ctrl + Break

### Автор
Варвара
> e-mail: upgradeki@yandex.ru

> telegram: @Varvara_Medok
