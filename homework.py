import logging
import os
import time

import requests
from dotenv import load_dotenv
from telebot import TeleBot

load_dotenv()


PRACTICUM_TOKEN = os.getenv('FIRST_TOKEN')
TELEGRAM_TOKEN = os.getenv('SECOND_TOKEN')
TELEGRAM_CHAT_ID = 6615343369

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if not all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        logger.critical('Отсутствует обязательная переменная окружения')
        return False
    return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram-чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Бот отправил сообщение: "{message}"')
    except Exception as error:
        logger.error(f'Ошибка при отправке сообщения в Telegram: {error}')


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params={'from_date': timestamp}
        )
        homework_statuses.raise_for_status()
        return homework_statuses.json()
    except requests.exceptions.HTTPError as error:
        logger.error(f'Ошибка доступа к API: {error}')
        return {}
    except Exception as error:
        logger.error(f'Неизвестная ошибка при запросе к API: {error}')
        return {}


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    expected_keys = ['homeworks', 'current_date']
    if not isinstance(response, dict):
        raise TypeError('Ответ API не является словарем')

    if 'homeworks' not in response or 'current_date' not in response:
        logger.error('Некорректный ответ от API, недостаток ключей')
        raise KeyError('Некорректный ответ от API')

    if not isinstance(response['homeworks'], list):
        logger.error('Ключ "homeworks" не является списком')
        raise TypeError('Ключ "homeworks" должен быть списком')

    for homework in response['homeworks']:
        expected_keys = [
            'id', 'status', 'homework_name',
            'reviewer_comment', 'date_updated', 'lesson_name'
        ]
        if not isinstance(homework, dict) or set(expected_keys) != set(homework.keys()):
            logger.error('Некорректная структура данных домашнего задания')
            raise ValueError('Некорректная структура данных домашнего задания')

        if 'status' not in homework or homework['status'] not in HOMEWORK_VERDICTS:
            logger.error('Недокументированный статус домашней работы')
            raise ValueError('Недокументированный статус домашней работы')



def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе."""
    if 'homework_name' not in homework:
        raise KeyError('Нет ключа homework_name в ответе API')

    homework_name = homework['homework_name']
    status = homework['status']

    if status not in HOMEWORK_VERDICTS:
        raise ValueError('Недокументированный статус домашней работы')

    verdict = HOMEWORK_VERDICTS[status]
    return f'Изменился статус проверки "{homework_name}": {verdict}'

def main():
    """Основная логика работы бота."""
    if not check_tokens():
        return

    bot = TeleBot(TELEGRAM_TOKEN)
    timestamp = int(time.time())


    while True:

        response = get_api_answer(timestamp)

        if response:
            try:
                homeworks = check_response(response)['homeworks']
                if homeworks:
                    for homework in homeworks:
                        message = parse_status(homework)
                        send_message(bot, message)
            except Exception as error:
                logger.error(f'Ошибка в основной программе: {error}')

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
