import json
import os

import requests
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

from keyboards import keyboard_weather

# Загрузка переменных и присвоение API-токена
load_dotenv('.env')
weather_token = os.getenv('WEATHER_API_TOKEN')


# Класс для хранения состояний
class Weather(StatesGroup):
    city = State()


async def weather(message: types.Message, state: FSMContext):
    """Инициирование событий прогноза погоды.

    Функция, которая запрашивает где отобразить погоду.
    """
    # Проверка типа чата
    if message.chat.type == 'private':
        # Если личная переписка, то запрашивается выбор: показать погоду по названию города или по запросу геолокации
        await message.answer('Где отобразить погоду?', reply_markup=keyboard_weather)
    else:
        # Если чат групповой, то в нем бот не может принимать геолокацию, поэтому запрашивает сразу город
        # Установка состояния ожидания ввода города от пользователя
        await state.set_state(Weather.city.state)
        await message.answer('Введите название города:', reply_markup=types.ReplyKeyboardRemove())


async def weather_set_city(message: types.Message, state: FSMContext):
    """Выбор города, где показать погоду.

    Функция, которая запрашивает наименование города, в котором нужно узнать погоду.
    """
    # Установка состояния ожидания ввода города от пользователя
    await state.set_state(Weather.city.state)
    await message.answer('Введите название города:', reply_markup=types.ReplyKeyboardRemove())


async def weather_city(message: types.Message, state: FSMContext):
    """Прогноз погода по названию города.

    Функция, которая принимает название города, проверяет прогноз погоды на стороннем сервере и выдает результат сообщением.
    """
    city = message.text
    # Обращение к API стороннего сайта для прогноза погоды
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&appid={weather_token}&units=metric'
    response = requests.get(url)
    status_code = response.status_code
    # Проверка на работоспособность сайта
    if status_code >= 300:
        await message.answer('Такого города не существует, либо сайт недоступен. Повторите попытку еще раз.')
        return
    # Преобразует входные текстовые данные JSON от сайта в формат Python
    data = json.loads(response.text)
    temp = data['main']['temp']
    desc = data['weather'][0]['description']
    # Вывод сообщения после успешного выполнения функции
    await message.answer(f'Температура в городе {city} сейчас {temp}°C {desc}.')
    # Закрытие хранилища данных FSM
    await state.finish()


async def weather_loc(message: types.Message):
    """Прогноз погода по геолокации.

    Функция, которая принимает геолокацию, проверяет прогноз погоды на стороннем сервере и выдает результат сообщением.
    """
    # Обработка входящего сообщения с геолокацией
    latitude = message['location']['latitude']
    longitude = message['location']['longitude']
    # Обращение к API стороннего сайта для прогноза погоды
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&lang=ru&appid={weather_token}&units=metric'
    response = requests.get(url)
    # Проверка на работоспособность сайта
    if response.status_code >= 300:
        await message.answer('Сайт недоступен. Повторите попытку позже.')
        return
    # Преобразует входные текстовые данные JSON от сайта в формат Python
    data = json.loads(response.text)
    temp = data['main']['temp']
    city = data['name']
    desc = data['weather'][0]['description']
    # Вывод сообщения после успешного выполнения функции
    await message.answer(f'Температура в вашем местоположении ({city}) сейчас {temp}°C {desc}.', reply_markup=types.ReplyKeyboardRemove())


def register_weather_handlers(dp: Dispatcher):
    """Регистрация обработчиков событий.

    Регистрирует все обработчики событий, связанные с прогнозом погоды.
    """
    dp.register_message_handler(weather_set_city, text=['Выбрать город'], state='*')
    dp.register_message_handler(weather, commands=['weather'])
    dp.register_message_handler(weather_city, state=Weather.city)
    dp.register_message_handler(weather_loc, content_types='location')
