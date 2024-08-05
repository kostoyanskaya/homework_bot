import logging
import os
import time
from http import HTTPStatus
import sys

from dotenv import load_dotenv
from telebot import TeleBot
import requests


load_dotenv()


PRACTICUM_TOKEN = os.getenv('FIRST_TOKEN')
TELEGRAM_TOKEN = os.getenv('SECOND_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

file_handler = logging.FileHandler(
    __file__ + '.log', encoding='UTF-8', mode='w'
)
stream_handler = logging.StreamHandler(
    sys.stdout
)


logging.basicConfig(
    level=logging.DEBUG,
    format=(
        '%(asctime)s - %(levelname)s - '
        '%(filename)s:%(lineno)d - %(message)s'
    ),
    handlers=[file_handler, stream_handler],
)

logger = logging.getLogger(__name__)


class InvalidResponseCodeError(Exception):
    """Кастомное исключение для неверного кода ответа."""

    def __init__(self, status_code, reason, text):
        """Конструктор класса InvalidResponseCodeError."""
        self.status_code = status_code
        self.reason = reason
        self.text = text
        super().__init__(
            f'Неверный код ответа: {status_code},'
            'Причина: {reason}, Текст: {text}'
        )


def check_tokens():
    """Проверяет доступность переменных окружения."""
    names_and_tokens = [
        ('PRACTICUM_TOKEN', 'FIRST_TOKEN'),
        ('TELEGRAM_TOKEN', 'SECOND_TOKEN'),
        ('TELEGRAM_CHAT_ID', 'TELEGRAM_CHAT_ID')
    ]
    try:
        for name, token in names_and_tokens:
            if not os.getenv(token):
                logger.critical(
                    f'Отсутствует обязательная переменная окружения {name}.'
                )
                return False
        return True

    except Exception as error:
        logger.error('Произошла ошибка: %s', error)
        return False


def send_message(bot, message):
    """Отправляет сообщение в Telegram-чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Бот отправил сообщение: "{message}"')
        return True
    except Exception as error:
        logger.error(f'Ошибка при отправке сообщения в Telegram: {error}')
        return False
    finally:
        logger.debug(f'Бот отправил сообщение: "{message}"')


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    params = dict(
        url=ENDPOINT,
        headers=HEADERS,
        params={"from_date": timestamp}
    )
    try:
        homework_statuses = requests.get(**params)
        if homework_statuses.status_code != HTTPStatus.OK:
            raise InvalidResponseCodeError(
                f'Stатус не равен 200: {homework_statuses.status_code}. '
                f'{homework_statuses.reason}'
            )
    except requests.exceptions.RequestException as error:
        raise ConnectionError(error)
    return homework_statuses.json()


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('Ответ API не является словарем')

    if 'homeworks' not in response:
        raise KeyError('Ключ homeworks отсутствует в ответе API')

    homeworks = response['homeworks']

    if not isinstance(homeworks, list):
        raise TypeError('Ключ homeworks должен быть списком')

    return homeworks


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе."""
    if 'homework_name' not in homework:
        raise KeyError('Нет ключа homework_name в API')
    homework_name = homework['homework_name']
    status = homework['status']
    if status not in HOMEWORK_VERDICTS:
        raise ValueError('Неожиданный статус домашней работы')

    verdict = HOMEWORK_VERDICTS[status]

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        sys.exit('Отсутствуют обязательные переменные окружения')

    bot = TeleBot(TELEGRAM_TOKEN)
    timestamp = int(time.time())

    last_message = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)

            if not homeworks:
                logger.debug('Нет новых статусов для отправки.')
            else:
                homework = homeworks[0]
                message = parse_status(homework)

                if message != last_message:
                    if send_message(bot, message):
                        last_message = message

            timestamp = response.get('current_date', timestamp)

        except Exception as error:
            current_message = f'Сбой в работе программы: {error}'
            logger.error(f'Ошибка при выполнении программы: {error}')
            if current_message != last_message:
                if send_message(bot, current_message):
                    last_message = current_message

        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
