from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from rmq.rabbit import send_to_queue
from aiogram import types

import telegram.app.keyboards as kb

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message):
    await message.reply('Привет!', reply_markup=kb.main)


@router.message()
async def handler_reminder(message: types.Message):  # для обработки входящих сообщений
    user_message = message.text
    print('id пользователя', message.from_user.id)
    correlation_id = str(message.chat.id)

    reply_queue = f'response_{message.chat.id}'

    await message.answer(f'Отпарвляю {user_message} на обработку...')

    await send_to_queue(user_message,
                        reply_to=reply_queue,
                        correlation_id=correlation_id,
                        routing_key='any_message')


@router.message()
async def handle_number(message: types.Message):
    try:
        number = int(message.text)
        # Сохраняем чистый chat.id без префикса
        correlation_id = str(message.chat.id)
        # Формируем имя очереди для ответа
        reply_queue = f"response_{message.chat.id}"

        await message.answer(f"⌛ Отправляю {number} на обработку...")
        # Передаем correlation_id и reply_queue отдельно
        await send_to_queue(number,
                            reply_to=reply_queue,
                            correlation_id=correlation_id,
                            routing_key='tasks')

    except ValueError:
        await message.answer("❌ Пожалуйста, отправьте целое число!")
