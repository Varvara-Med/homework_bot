import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

PRACTICUM_TOKEN = os.getenv('token')
TELEGRAM_TOKEN = os.getenv('varvara_token')
TELEGRAM_CHAT_ID = os.getenv('chat_id')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
PAYLOAD = {'from_date': 0}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляем сообщение в терминал и в чат телеграмм."""
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        logging.info('Сообщение отправлено')
        return bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        logging.error(f'Сообщение не отправлено {e}', exc_info=True)


def get_api_answer(current_timestamp):
    """Отправляем запрос к API сервиса и получаем ответ в формате .json."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        api_answer = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception as e:
        logging.error(f'Не удалось получить доступ к API {e}', exc_info=True)
    if api_answer.status_code != 200:
        api_answer.raise_for_status()
    else:
        return api_answer.json()


def check_response(response):
    """Проверяет, что ответ API соответствует ожиданиям."""
    try:
        hw_list = response['homeworks']
    except KeyError as e:
        message = f'Не найден ключ homeworks: {e}'
        logging.error(message)
    if not isinstance(hw_list, list):
        message = 'Перечень домашки не является списком'
        logging.error(message)
        raise Exception(message)
    if hw_list is None:
        message = 'Не найден словарь с домашкой'
        logging.error(message)
        raise Exception(message)
    return hw_list


def parse_status(homework):
    """Извлекает статус домашки."""
    try:
        homework_name = homework.get('homework_name')
    except KeyError as e:
        e_message = f'Нет ключа homework_name {e}'
        logging.error(e_message)
        raise Exception(e_message)
    try:
        homework_status = homework.get('status')
    except KeyError as e:
        e_message = f'Нет ключа status {e}'
        logging.error(e_message)
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения.
    Если отсутствует какая-то переменная - функция возвращает False.
    """
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    else:
        logging.critical('Проверь доступность переменных окружения!')
        return False


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            if not response.get('homeworks'):
                time.sleep(RETRY_TIME)
                continue
            if check_response(response):
                homework = response.get('homeworks')[0]
                message = parse_status(homework)
                send_message(bot, message)
            current_timestamp = response.get('current_date')
            logger.info('Домашка не проверена')
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.exception(f'Сбой в работе программы: {error}')
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
