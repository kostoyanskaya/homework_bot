# Bot Assistant
python telegram bot
### Bot features:
- Every 10 minutes, it polls the Praktikum.Homework service API and checks the status of the homework sent for review.
- When the status is updated, it analyzes the API response and sends you a corresponding notification in Telegram.
- Logs its work and informs you about important issues via a Telegram message.
  
## Installation
1. Clone the repository:
    ```python
    git clone git@github.com:kostoyanskaya/homework_bot.git
    ```
2. Navigate to the project folder:
    ```python
    cd homework_bot/
    ```
3. Set up a virtual environment for the project:
    ```python
    python -m venv venv
    ```
4. Activate the virtual environment for the project:
    ```python
    # for Linux and MacOS
    source venv/bin/activate
    # for Windows
    source venv/Scripts/activate
    ```
5. Install dependencies:
    ```python
    python3 -m pip install --upgrade pip
    pip install -r requirements.txt
    ```
7. Register the chat bot in Telegram
8. Create a .env file in the root directory to store environment variables
    ```python
    PRAKTIKUM_TOKEN = 'xxx'
    TELEGRAM_TOKEN = 'xxx'
    TELEGRAM_CHAT_ID = 'xxx'
    ```
8. Run the project locally:
    ```python
    # for Linux and MacOS
    python homework_bot.py
    # for Windows
    python3 homework_bot.py
    ```
## Technologies
![python version](https://img.shields.io/badge/Python-3.9-yellowgreen?logo=python)
![python-telegram-bot version](https://img.shields.io/badge/telegram_bot-13.7-yellowgreen?logo=telegram)
![requests version](https://img.shields.io/badge/requests-2.26-yellowgreen)
## Author
#### [_Victoria_](https://github.com/kostoyanskaya/)
