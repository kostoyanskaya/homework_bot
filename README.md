# Бот-ассистент
python telegram bot
### Возможности бота:
- Раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы.
- При обновлении статуса анализирует ответ API и отправляет вам соответствующее уведомление в Telegram.
- Логгирует свою работу и сообщает вам о важных проблемах сообщением в Telegram.
  
## Установка

1. Клонировать репозиторий:

    ```python
    git clone git@github.com:kostoyanskaya/homework_bot.git
    ```

2. Перейти в папку с проектом:

    ```python
    cd homework_bot/
    ```

3. Установить виртуальное окружение для проекта:

    ```python
    python -m venv venv
    ```

4. Активировать виртуальное окружение для проекта:

    ```python
    # для OS Lunix и MacOS
    source venv/bin/activate

    # для OS Windows
    source venv/Scripts/activate
    ```

5. Установить зависимости:

    ```python
    python3 -m pip install --upgrade pip
    pip install -r requirements.txt
    ```

7. Зарегистрировать чат-бота в Телеграм

8. Создать в корневой директории файл .env для хранения переменных окружения

    ```python
    PRAKTIKUM_TOKEN = 'xxx'
    TELEGRAM_TOKEN = 'xxx'
    TELEGRAM_CHAT_ID = 'xxx'
    ```

8. Запустить проект локально:

    ```python
    # для OS Lunix и MacOS
    python homework_bot.py

    # для OS Windows
    python3 homework_bot.py
    ```
## Технологии
![python version](https://img.shields.io/badge/Python-3.9-yellowgreen?logo=python)
![python-telegram-bot version](https://img.shields.io/badge/telegram_bot-13.7-yellowgreen?logo=telegram)
![requests version](https://img.shields.io/badge/requests-2.26-yellowgreen)
## Автор
#### [_Анастасия Ресницкая_](https://github.com/kostoyanskaya/)
