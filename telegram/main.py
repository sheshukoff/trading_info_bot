from aiogram import Bot, Dispatcher, types, Router
from rmq.rabbit import send_to_queue, setup_consumer
import asyncio
import logging
from telegram.app import keyboards as kb
from aiogram.types import Message
from aiogram.filters import CommandStart
from dotenv import dotenv_values

config = dotenv_values("../.env")

BOT_TOKEN = config.get("BOT_TOKEN")


logging.basicConfig(level=logging.INFO)

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
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

