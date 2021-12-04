import logging
from logging.handlers import RotatingFileHandler
import os
import time

import requests
import telegram
from dotenv import load_dotenv

import exceptions

from http import HTTPStatus


load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    encoding='utf-8',
    filename='main.log',
    filemode='a')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('my_logger.log',
                              maxBytes=50000000,
                              backupCount=5,
                              encoding='utf-8'
                              )
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

handler.setFormatter(formatter)


PRACTICUM_TOKEN = os.getenv('TOKEN')
TELEGRAM_TOKEN = os.getenv('VARVARA_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
PAYLOAD = {'from_date': 0}


HOMEWORK_VERDICT = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляем сообщение в терминал и в чат телеграмм."""
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        logger.info('Сообщение отправлено')
        return bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        logger.error(f'Сообщение не отправлено {e}', exc_info=True)


def get_api_answer(current_timestamp):
    """Отправляем запрос к API сервиса и получаем ответ в формате .json."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        api_answer = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception as e:
        logger.error(f'Не удалось получить доступ к API {e}', exc_info=True)
        raise exceptions.NegativeApiAccess('Не удалось получить доступ к API')
    if api_answer.status_code != HTTPStatus.OK:
        raise exceptions.NegativeApiStatus('Код ответа не 200')
    return api_answer.json()


def check_response(response):
    """Проверяет, что ответ API соответствует ожиданиям."""
    try:
        hw_list = response['homeworks']
    except KeyError as e:
        message = f'Не найден ключ homeworks: {e}'
        logger.error(message)
        raise KeyError(message)
    if not isinstance(hw_list, list):
        message = 'Перечень домашки не является списком'
        logger.error(message)
        raise Exception(message)
    if hw_list is None:
        message = 'Не найден словарь с домашкой'
        logger.error(message)
        raise Exception(message)
    return hw_list


def parse_status(homework):
    """Извлекает статус домашки."""
    try:
        homework_name = homework['homework_name']
    except KeyError as e:
        e_message = f'Нет ключа homework_name {e}'
        logger.error(e_message)
        raise KeyError(e_message)
    try:
        homework_status = homework['status']
    except KeyError as e:
        e_message = f'Нет ключа status {e}'
        logger.error(e_message)
        raise KeyError(e_message)
    verdict = HOMEWORK_VERDICT[homework_status]
    if verdict is KeyError:
        verdict = 'Пришёл несуществующий статус.'
        logger.error(verdict)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения.
    Если отсутствует какая-то переменная - функция возвращает False.
    """
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    logger.critical('Проверь доступность переменных окружения!')
    return False


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    # current_timestamp = 1
    last_response = 0
    while True:
        try:
            response = get_api_answer(current_timestamp)
            if not response.get('homeworks'):
                time.sleep(RETRY_TIME)
                continue
            check_response(response)
            if response != last_response:
                last_response = response
                homework = response.get('homeworks')[0]
                message = parse_status(homework)
                send_message(bot, message)
            current_timestamp = response.get('current_date')
            logger.info('Домашка не проверена')
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.exception(f'Сбой в работе программы: {error}')
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
