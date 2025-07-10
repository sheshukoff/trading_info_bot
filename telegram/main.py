from aiogram import Bot, Dispatcher
import asyncio
import logging

from rmq.rabbit import setup_consumer
from dotenv import dotenv_values
from telegram.app.handlers import router

config = dotenv_values("../.env")
BOT_TOKEN = config.get("BOT_TOKEN")


logging.basicConfig(level=logging.INFO)

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


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

