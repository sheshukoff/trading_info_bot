import asyncio
import logging
import json
import aiorabbit
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart

from aiogram.exceptions import TelegramForbiddenError, TelegramNotFound
from aiogram_dialog import Dialog, setup_dialogs

from dotenv import dotenv_values
from telegram.handlers import router, start
from telegram.windows_for_dialogs import (
    window_start, window_disclaimer, window_strategy, window_coins, window_alarm_times, window_ack_strategy, window_confirmation
)
from api import delete_user
from telegram.handlers import reports

config = dotenv_values("../.env")
RABBITMQ_URL = config.get("RABBITMQ_URL")

config = dotenv_values("../.env")
BOT_TOKEN = config.get("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

dialog = Dialog(
    window_start, window_disclaimer, window_strategy, window_coins, window_alarm_times, window_ack_strategy, window_confirmation
)

bad_chat_ids = []


async def iterate_chat_ids(chat_ids):
    for chat_id in chat_ids:
        await asyncio.sleep(0)
        yield chat_id


async def unnecessary_chat_id(bad_chat_ids: list, chat_ids: list):
    for bad_id in bad_chat_ids:
        if bad_id in chat_ids:
            chat_ids.remove(bad_id)


async def send_message(chat_id: int, notification: str, report: str):
    try:
        await bot.send_message(chat_id=chat_id, text=notification, parse_mode="HTML")
    except TelegramForbiddenError:
        print(f"Пользователь c чатом id {chat_id} заблокировал бота.")
        bad_chat_ids.append(chat_id)
        await delete_user(chat_id)
    except TelegramNotFound:
        print(f"Пользователь c чатом id {chat_id} не найден (удалён или не писал боту)")
        bad_chat_ids.append(chat_id)
        await delete_user(chat_id)


async def unpacking_message(message: json) -> tuple:
    result = json.loads(message.body.decode("utf-8"))

    notification = result.get('message')  # сам отчет
    report = result.get('report')  # по чем отчет

    strategies = reports.get('strategies')

    chat_ids = strategies.get(report)

    return notification, report, chat_ids


async def return_message():
    try:
        async with aiorabbit.connect(RABBITMQ_URL) as client:
            print('Подключено')
            await client.queue_declare('periodic_queue')  # Создание очереди
            async for message in client.consume('periodic_queue'):  # достаю из очереди по одному сообщению

                notification, report, chat_ids = await unpacking_message(message)

                if chat_ids:
                    async for chat_id in iterate_chat_ids(chat_ids):
                        await send_message(chat_id, notification, report)

                strategies = reports.get('strategies')
                chat_ids = strategies.get(report)

                await unnecessary_chat_id(bad_chat_ids, chat_ids)

                if message.delivery_tag:
                    await client.basic_ack(message.delivery_tag)
                print(strategies.get(report), 'должен оказаться пустым после блокировки бота')
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
# Отредактировать отображение цены где монета стоит очень мало например PEPE-USDT редактировать в strategy
# Telegram server says - Bad Request: chat not found если приходит такое сообщение то пользователя удалить из БД
# По чистить код от принтов
# Оставляю reports так как будет работать быстрее, БД для хранения
# До 10 пользователей то окей пойдет просто меняю через БД, количество подключаемых стратегий (Дальше разный уровень пользователя)
# Делаем FAST API надо посмотреть про API
