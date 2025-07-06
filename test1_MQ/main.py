from aiogram import Bot, Dispatcher, types, Router, F
from config import Config
from rabbit import send_to_queue, setup_consumer
import asyncio
import logging
import keyboars as kb
from aiogram.types import Message
from aiogram.filters import CommandStart

logging.basicConfig(level=logging.INFO)

bot = Bot(Config.BOT_TOKEN)
dp = Dispatcher()
router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message):
    await message.reply('Привет!', reply_markup=kb.main)


# @router.callback_query(F.data == 'catalog')
# async def catalog(callback: CallbackQuery):
#     await callback.answer('Вы выбрали каталог')
#     await callback.message.edit_text('Привет!', reply_markup=kb.main)


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


async def main():
    dp.include_router(router)

    # Передаем экземпляр bot вместо dp
    rmq_connection = await setup_consumer(bot)

    # Запуск бота
    await dp.start_polling(bot)

    # При завершении закрываем соединение
    print('закрываем соединение rmq')
    await rmq_connection.close()


if __name__ == "__main__":
    asyncio.run(main())

# user -> 5 -> aiogram (main.py) -> RabbitMQ -> worker (worker.py) ->
# -> RabbitMQ -> aiogram (main.py) -> user -> result (25)

# core.py -> RabbitMQ -> aiogram (run.py) -> user (message)

# redis


# Run:
# 1. rabbitmq in docker
# 2. worker.py
# 3. main.py (aiogram)

# RabbitMQ default login/pass = guest

# сингнал - не нужна очередь ответов
# новости - не нужна очередь ответов
# входящие сообщения (торговать) - нужна очередь ответов

# пришел сингал - подтвеждение - открыть позицию
# пришел сингал - подтвеждение - закрыть позицию


# убрать все лишнее почистить код print пока оставлю
