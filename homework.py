import logging
import os
import time
from http import HTTPStatus

from dotenv import load_dotenv
from telebot import TeleBot
import requests


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
    params = dict(
        url=ENDPOINT,
        headers=HEADERS,
        params={"from_date": timestamp}
    )
    try:
        homework_statuses = requests.get(**params)
    except Exception as error:
        logger.error(f"Ошибка при запросе к API: {error}")
    else:
        if homework_statuses.status_code != HTTPStatus.OK:
            raise requests.HTTPError('Статус страницы не равен 200')
        return homework_statuses.json()


def check_response(response):
    if not isinstance(response, dict):
        logger.error('Ответ API не является словарем')
        raise TypeError('Ответ API не является словарем')

    if 'homeworks' not in response:
        logger.error('Ключ homeworks отсутствует в ответе API')
        raise KeyError('Ключ homeworks отсутствует в ответе API')

    if 'current_date' not in response:
        logger.error('Ключ current_date отсутствует в ответе API')
        raise KeyError('Ключ current_date отсутствует в ответе API')

    homeworks = response.get('homeworks', [])

    if not isinstance(homeworks, list):
        logger.error('Ключ homeworks не является списком')
        raise TypeError('Ключ homeworks должен быть списком')

    for homework in homeworks:
        expected_keys = [
            'id', 'status', 'homework_name',
            'reviewer_comment', 'date_updated', 'lesson_name'
        ]
        if not isinstance(homework, dict) or set(
            expected_keys
        ) != set(homework.keys()):
            logger.error('Некорректная структура данных')
            raise ValueError('Некорректная структура данных')

        if homework['status'] not in HOMEWORK_VERDICTS:
            logger.error('Ошибка статуса работы')
            raise ValueError('Ошибка статуса работы')

    return response


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе."""
    if 'homework_name' not in homework:
        raise KeyError('Нет ключа homework_name в API')

    homework_name = homework['homework_name']
    status = homework['status']

    if status not in HOMEWORK_VERDICTS:
        raise ValueError('Неправильный статус домашней работы')

    verdict = HOMEWORK_VERDICTS.get(status, None)
    if verdict:
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    return None


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        return

    bot = TeleBot(TELEGRAM_TOKEN)
    timestamp = int(time.time())

    error_sent = False

    while True:
        try:
            response = get_api_answer(timestamp)

            if check_response(response):
                for homework in response['homeworks']:
                    message = parse_status(homework)
                    if message:
                        send_message(bot, message)

                if not response['homeworks']:
                    logger.debug('Нет новых статусов для отправки.')

            timestamp = response.get('current_date', timestamp)

        except Exception as error:
            if not error_sent:
                message = f'Сбой в работе программы: {error}'
                send_message(bot, message)
                error_sent = True
            logger.error(f'Ошибка при выполнении программы: {error}')

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
