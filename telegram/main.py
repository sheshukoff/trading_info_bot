import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart


from aiogram_dialog import Dialog, setup_dialogs

from dotenv import dotenv_values
from telegram.handlers import router, start
from telegram.windows_for_dialogs import (
    window_start, window_disclaimer, window_strategy, window_coins, window_alarm_times, window_confirmation
)
from rmq.rabbit import setup_consumer

dialog = Dialog(
    window_start, window_disclaimer, window_strategy, window_coins, window_alarm_times, window_confirmation
)


async def main():
    logging.basicConfig(level=logging.INFO)
    config = dotenv_values("../.env")
    BOT_TOKEN = config.get("BOT_TOKEN")
    bot = Bot(token=BOT_TOKEN)

    rmq_connection = await setup_consumer(bot)
    dp = Dispatcher()
    dp.include_router(dialog)
    dp.include_router(router)
    dp.message.register(start, CommandStart())

    setup_dialogs(dp)
    await dp.start_polling(bot)
    await rmq_connection.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')

# Планы на сегодня:
# Закончить добавление стратегии
# Затем запусктить эти стратегии в работу
# По возможности сделать вывод информации (что делать покупать или продавать)
