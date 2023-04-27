from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


# Клавиатура для выбора способов отображения погоды
keyboard_weather = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Выбрать город'),
            KeyboardButton(text='Геолокация', request_location=True),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите способ',
)


# Клавиатура для выбора наиболее известных валют
keyboard_currency = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='EUR'),
            KeyboardButton(text='USD'),
            KeyboardButton(text='RUB'),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите валюту или введите свою',
)
