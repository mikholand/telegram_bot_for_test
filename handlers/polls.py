import random

from aiogram import Dispatcher, types

from config import answers, questions


async def send_poll_to_group(message: types.Message):
    """Отправка опроса в групповой чат.

    Функция отправляет в групповой чат один из 10 вопросов с 4 вариантами ответов.
    """
    # Проверка типа чата на групповой
    if message.chat.type == 'group':
        # Генерация случайного числа (количество всех вопросов)
        option = random.randint(0, len(questions) - 1)
        # Отправка рандомного опроса в групповой чат
        await message.answer_poll(question=questions[option],
                                  options=answers[option])
    else:
        # Если чат не групповой, то отправляется сообщение указывающее на это
        await message.answer('Опросы могут быть отправлены только в групповой чат.')


def register_polls_handlers(dp: Dispatcher):
    """Регистрация обработчиков событий.

    Регистрирует все обработчики событий, связанные с опросами.
    """
    dp.register_message_handler(send_poll_to_group, commands=['poll'])
