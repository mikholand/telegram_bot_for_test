import json
import os

import requests
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

from config import all_currency
from keyboards import keyboard_currency

# Загрузка переменных и присвоение API-токена
load_dotenv('.env')
cur_token = os.getenv('CURRENCY_API_TOKEN')


# Класс для хранения состояний
class Currency(StatesGroup):
    currency_amount = State()
    currency_from = State()
    currency_to = State()


def is_number(str: str):
    """Проверка числа.

    Функция проверяет, является ли строка вещественным числом.

    Args:
        str (str): Строка, которую необходимо проверить.

    Returns:
        bool: True, если строку можно преобразовать в вещественное число, иначе False.
    """
    try:
        float(str)
        return True
    except ValueError:
        return False


async def set_amount(message: types.Message, state: FSMContext):
    """Инициирование событий конвертации.

    Функция, которая запрашивает количество валюты, которое нужно обменять.
    """
    # Установка состояния ожидания ввода числа от пользователя
    await state.set_state(Currency.currency_amount.state)
    await message.answer('Какое количество вам нужно обменять? Введите нужное число (например, 100.51):')


async def set_from(message: types.Message, state: FSMContext):
    """Выбор валюты, которую нужно обменять.

    Функция, которая запрашивает краткое наименование валюты, которую нужно обменять.
    """
    # Проверка, ввел ли пользователь число
    if not is_number(message.text):
        # Если пользователь ввел не число или число с ошибкой, то ему придет сообщение, чтобы он ввел корректное значение
        await message.answer('Ошибка. Пожалуйста, введите целое или вещественное число (например, 100 или 25.78):')
        return
    # Сохранение числа в хранилище данных FSM
    await state.update_data(currency_amount=message.text)
    # Установка состояния ожидания ввода валюты от пользователя, которую меняют
    await state.set_state(Currency.currency_from.state)
    await message.answer('Выберете валюту или введите свою, которую меняете (например, EUR):', reply_markup=keyboard_currency)


async def set_to(message: types.Message, state: FSMContext):
    """Выбор валюты, на которую нужно обменять.

    Функция, которая запрашивает краткое наименование валюты, на которую нужно обменять.
    """
    # Преобразовываем сообщение в верхний регистр
    cur_up_from = message.text.upper()
    # Проверка, ввел ли пользователь корректную валюту
    if cur_up_from not in all_currency:
        await message.answer('Такой валюты не существует. Введите валюту из списка: ' + ', '.join(all_currency), reply_markup=keyboard_currency)
        return
    # Сохранение валюты в хранилище данных FSM
    await state.update_data(currency_from=cur_up_from)
    # Установка состояния ожидания ввода валюты от пользователя, на которую меняют
    await state.set_state(Currency.currency_to.state)
    await message.answer('Выберете валюту или введите свою, на которую меняете (например, USD):', reply_markup=keyboard_currency)


async def converting(message: types.Message, state: FSMContext):
    """Конвертация валюты.

    Функция, которая использует все раннее введенные данные, конвертирует валюту на стороннем сервере и выдает результат сообщением.
    """
    # Преобразовываем сообщение в верхний регистр
    cur_up_to = message.text.upper()
    # Проверка, ввел ли пользователь корректную валюту
    if cur_up_to not in all_currency:
        await message.answer('Такой валюты не существует. Введите валюту из списка: ' + ', '.join(all_currency), reply_markup=keyboard_currency)
        return
    # Сохранение валюты в хранилище данных FSM
    await state.update_data(currency_to=cur_up_to)
    # Получение всех раннее введенных данных
    currency_data = await state.get_data()
    # Присвоение всех значений данных переменным
    currency_amount = currency_data['currency_amount']
    currency_from = currency_data['currency_from']
    currency_to = currency_data['currency_to']

    # Обращение к API стороннего сайта для конвертации валюты
    payload = {}
    headers = {
        'apikey': cur_token
    }
    url = f'https://api.apilayer.com/exchangerates_data/convert?to={currency_to}&from={currency_from}&amount={currency_amount}'
    # Получение ответа от GET запроса к сайту
    response = requests.request('GET', url, headers=headers, data=payload)
    # Проверка на работоспособность сайта
    if response.status_code > 300:
        await message.answer('К сожалению, сайт с конвертацией валюты сейчас не доступен.', reply_markup=types.ReplyKeyboardRemove())
        return
    # Преобразует входные текстовые данные JSON от сайта в формат Python
    data = json.loads(response.text)
    # Курс валют
    rate = data['info']['rate']
    # Готовый результат при конвертации
    result = data['result']
    # Вывод сообщения после успешного выполнения функции
    await message.answer(f'Курс на текущий момент:\n'
                         f'1 {currency_from} = {rate} {currency_to}.\n\n'
                         f'Ваша конвертация:\n'
                         f'{currency_amount} {currency_from} = {result} {currency_to}.', reply_markup=types.ReplyKeyboardRemove())
    # Закрытие хранилища данных FSM
    await state.finish()


def register_currency_handlers(dp: Dispatcher):
    """Регистрация обработчиков событий.

    Регистрирует все обработчики событий, связанные с конвертацией валюты.
    """
    dp.register_message_handler(set_amount, commands=['currency'], state='*')
    dp.register_message_handler(set_from, state=Currency.currency_amount)
    dp.register_message_handler(set_to, state=Currency.currency_from)
    dp.register_message_handler(converting, state=Currency.currency_to)
