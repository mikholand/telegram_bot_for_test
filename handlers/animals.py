import json

import requests
from aiogram import Dispatcher, types


async def photo_animals(message: types.Message):
    """Отправка фото животных.

    Функция, которая получает по API фото котиков и отправляет его пользователю.
    """
    # Переменной url присваивается список из 2 сайтов, которые предоставляют фото котиков
    url = ['https://cataas.com/cat?json=true',
           'https://api.thecatapi.com/v1/images/search?mime_types=jpg,png']
    # GET запрос к первому сайту
    response = requests.get(url[0])
    # Проверка на работоспособность сайта
    if response.status_code == 200:
        # Если все хорошо, то обрабатываем запрос и получаем полный url с фотографией
        data = json.loads(response.text)
        image_url = 'https://cataas.com' + data['url']
    else:
        # Если первый сайт не отвечает, то повторяем туже процедуру со вторым сайтом
        response = requests.get(url[1])
        if response.status_code == 200:
            data = json.loads(response.text)
            image_url = data[0]['url']
        else:
            # В противном случае делаем переменную пустой
            image_url = None

    # Проверяем переменную на наличие url котиков
    if image_url:
        # Если url есть, то пользователю отправляется фото
        await message.answer_photo(image_url)
    else:
        # Если url нет, то пользователю отправляется сообщение, что сайты недоступны
        await message.answer('К сожалению, сайты с животными сейчас не доступны.')


def register_animals_handlers(dp: Dispatcher):
    """Регистрация обработчиков событий.

    Регистрирует все обработчики событий, связанные с животными.
    """
    dp.register_message_handler(photo_animals, commands=['animals'])
