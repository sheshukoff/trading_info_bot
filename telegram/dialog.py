import asyncio
import logging
import aiorabbit
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart


from aiogram_dialog import Dialog, setup_dialogs

from dotenv import dotenv_values
from telegram.handlers import router, start
from telegram.windows_for_dialogs import (
    window_start, window_disclaimer, window_strategy, window_coins, window_alarm_times, window_ack_strategy, window_confirmation
)

config = dotenv_values("../.env")
RABBITMQ_URL = config.get("RABBITMQ_URL")

config = dotenv_values("../.env")
BOT_TOKEN = config.get("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

dialog = Dialog(
    window_start, window_disclaimer, window_strategy, window_coins, window_alarm_times, window_ack_strategy, window_confirmation
)

CHAT_ID = ['251147722', '5104570308']

# T = {:}


async def return_message():
    try:
        async with aiorabbit.connect(RABBITMQ_URL) as client:
            print('Подключено')
            await client.queue_declare('periodic_queue')  # Создание очереди
            async for message in client.consume('periodic_queue'):  # достаю из очереди по одному сообщению
                result = message.body.decode()
                print(result)

                # async for chat_id in CHAT_ID:
                await bot.send_message(chat_id='5104570308', text=result)  # 5104570308
                # await bot.send_message(chat_id='251147722', text=result)

                if message.delivery_tag:
                    await client.basic_ack(message.delivery_tag)
    except Exception as error:
        print(error)


async def main():
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()

    dp.include_router(dialog)
    dp.include_router(router)
    dp.message.register(start, CommandStart())

    setup_dialogs(dp)
    # await dp.start_polling(bot)

    tasks = [
        asyncio.create_task(dp.start_polling(bot)),
        asyncio.create_task(return_message())
    ]

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')


# Планы на сегодня:
# Закончить добавление стратегии
# Затем запусктить эти стратегии в работу
# По возможности сделать вывод информации (что делать покупать или продавать)
