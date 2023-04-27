import os

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

import handlers


def register_handlers(dp: Dispatcher):
    """Регистрация хендлеров.

    Функция, которая регистрирует все хендлеры.
    """
    handlers.register_common_handlers(dp)
    handlers.register_animals_handlers(dp)
    handlers.register_currency_handlers(dp)
    handlers.register_polls_handlers(dp)
    handlers.register_weather_handlers(dp)


# Загрузка переменных и присвоение API-токена
load_dotenv('.env')
bot_token = os.getenv('BOT_API_TOKEN')

# Инициализация бота
bot = Bot(bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Регистрация всех обработчиков событий
register_handlers(dp)


if __name__ == '__main__':
    executor.start_polling(dp)
