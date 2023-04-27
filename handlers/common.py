from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text


async def start(message: types.Message, state: FSMContext):
    """Стартовая функция.

    Закрывает все состояния, если они были и отправляет приветственное сообщение.
    """
    await state.finish()
    await message.answer('Привет! Я бот, который может выполнить следующие функции:\n\n'
                         '1. /weather - Определить текущую погоду в определенном городе.\n'
                         '2. /currency - Конвертировать валюты.\n'
                         '3. /animals - Отправить случайную картинку с милыми животными.\n'
                         '4. /poll - Создать опрос в групповом чате.\n'
                         '5. /cancel или "Отмена" - Отменить текущее действие.')


async def cancel(message: types.Message, state: FSMContext):
    """Функция отмены.

    Закрывает все состояния, если они были и отправляет подтверждение прекращения действий.
    """
    await state.finish()
    await message.answer('Действие отменено', reply_markup=types.ReplyKeyboardRemove())


def register_common_handlers(dp: Dispatcher):
    """Регистрация обработчиков событий.

    Регистрирует все общие обработчики событий.
    """
    dp.register_message_handler(start, commands=['start', 'help'], state='*')
    dp.register_message_handler(cancel, commands=['cancel'], state='*')
    dp.register_message_handler(cancel, Text(equals='отмена', ignore_case=True), state='*')
