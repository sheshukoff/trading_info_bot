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
    window_start, window_disclaimer, window_strategy, window_coins,
    window_alarm_times, window_ack_strategy, window_confirmation,
    window_remove_strategies, window_ack_remove_strategies, window_repeat_strategy, window_strategy_limit
)
import telegram.api as tg_api
from telegram.handlers import reports
from connection_oracle.delete_queries import delete_user_all_strategies
from connection_oracle.get_queries import get_data_for_stop_scheduler

config = dotenv_values("../.env")
RABBITMQ_URL = config.get("RABBITMQ_URL")

config = dotenv_values("../.env")
BOT_TOKEN = config.get("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

dialog = Dialog(
    window_start,
    window_disclaimer,
    window_strategy,
    window_coins,
    window_alarm_times,
    window_ack_strategy,
    window_confirmation,
    window_remove_strategies,
    window_ack_remove_strategies,
    window_repeat_strategy,
    window_strategy_limit
)

bad_chat_ids = []


async def stop_scheduler(chat_id):
    try:
        un_use_data = await get_data_for_stop_scheduler(chat_id)
        if un_use_data:
            for ticker, timeframe in un_use_data:
                job_id = f'{ticker} {timeframe}'
                await tg_api.delete_job(job_id)
    except Exception as e:
        print(f"Ошибка при очистке scheduler: {e}")


async def handle_blocked_user(chat_id):
    try:
        await tg_api.delete_all_user_strategy(chat_id)
        await tg_api.delete_user(chat_id)
        print(f"Пользователь {chat_id} полностью удалён")
    except Exception as e:
        print(f"Ошибка при удалении пользователя {chat_id}: {e}")


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
    except (TelegramForbiddenError, TelegramNotFound):
        print(f"Пользователь c чатом id {chat_id} заблокировал бота.")
        await stop_scheduler(chat_id)
        await handle_blocked_user(chat_id)


async def unpacking_message(message: json) -> tuple:
    result = json.loads(message.body.decode("utf-8"))

    notification = result.get('message')  # сам отчет
    report = result.get('report')  # по чем отчет

    chat_ids = reports.get_strategy_users(report)

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

                chat_ids = reports.get_strategy_users(report)
                print('чаты id', chat_ids)

                await unnecessary_chat_id(bad_chat_ids, chat_ids)

                if message.delivery_tag:
                    await client.basic_ack(message.delivery_tag)
                print(reports.get_strategy_users(report), 'должен оказаться пустым после блокировки бота')

                # После того как список остался пустым нужно остановить task планировщик
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