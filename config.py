# file: config.py
from os import environ
from dotenv import load_dotenv

# Загрузка значений переменных окружения из .env
load_dotenv()

API_ID = environ.get('API_ID')
API_HASH = environ.get('API_HASH')
SESSION_STRING = environ.get('SESSION_STRING')
DATABASE_URL = 'databases/chats.db'

ADMIN_ID = environ.get('ADMIN_ID')
CLIENT_ID = environ.get('CLIENT_ID')
ADMIN_NICK = environ.get('ADMIN_NICK')

ADMIN_ID = int(ADMIN_ID)
CLIENT_ID = int(CLIENT_ID)