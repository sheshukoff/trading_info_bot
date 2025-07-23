import time
from connection_okx.get_data import safe_to_csv_file
from .scheduler import Scheduler
import asyncio
import random

SCHEDULERS = {}


async def add_scheduler(scheduler_dict, function, ticker, timeframe):
    key = f"{ticker}_{timeframe}"
    if key in scheduler_dict.keys():
        print(f"⛔ Задача {key} уже существует, не добавляем.")
        return scheduler_dict.get(key)

    s = await Scheduler.create(function, timeframe, ticker=ticker, timeframe=timeframe)
    scheduler_dict[key] = s
    print(f"✅ Добавлена задача: {key}")
    return s


async def main():
    # Список монет (можешь дополнить своими)
    coins = ["BTC-USDT", "SOL-USDT", "XRP-USDT"]  # "SOL-USDT", "XRP-USDT"

    # Список таймфреймов (например, как на биржах или в TradingView)
    timeframes = ["1m", "4H", "1D"]  # "4H", "1D"

    pairs = [(coin, tf) for coin in coins for tf in timeframes]
    print(pairs)

    count = 0

    while count < 5:
        random_element = random.choice(pairs)
        ticker, timeframe = random_element
        await add_scheduler(SCHEDULERS, safe_to_csv_file, ticker, timeframe)
        await asyncio.sleep(1)
        count += 1
        print(len(SCHEDULERS))
        print(SCHEDULERS.keys())

    print(len(SCHEDULERS.keys()))

    run_tasks = []
    for scheduler in SCHEDULERS.values():
        run_tasks.append(scheduler.run_async())

        print('run_tasks', run_tasks)

    await asyncio.gather(*run_tasks)


if __name__ == '__main__':
    asyncio.run(main())

# class Scheduler:
#     # Атрибуты
#     __ALARM_TIMES = {
#         '1m': [f"{__h:02d}:{__m:02d}:00" for __h in range(24) for __m in range(60)],
#         '5m': [f"{__h:02d}:{__m:02d}:00" for __h in range(24) for __m in range(0, 60, 5)],
#         '15m': [f"{__h:02d}:{__m:02d}:00" for __h in range(24) for __m in range(0, 60, 15)],
#         '30m': [f"{__h:02d}:{__m:02d}:00" for __h in range(24) for __m in range(0, 60, 30)],
#         '1H': [f"{__h:02d}:00:00" for __h in range(24)],
#         '4H': [f'{__h:02d}:00:00' for __h in range(3, 24, 4)],
#         '1D': ['03:00:00']
#     }
#
#     def __init__(self, function, interval, **kwargs):
#         self.__function = function
#         self.__interval = interval
#         self.__kwargs = kwargs
#
#         self.__setup_alarm_times()
#
#     def __setup_alarm_times(self):
#         try:
#             times = self.__ALARM_TIMES[self.__interval]
#             # print(f'Работаю по интевалу {self.__interval}')
#             for work_time in times:
#                 job = partial(self.__function, **self.__kwargs)
#                 schedule.every().day.at(work_time).do(job)
#             # print('Время работы раставлено')
#         except KeyError:
#             print(f'❌ Такого таймфрейма нет: {self.__interval}')
#
#     def run(self):
#         try:
#             while True:
#                 schedule.run_pending()
#                 time.sleep(1)
#         except KeyboardInterrupt:
#             print('Exit')

#
#
# if __name__ == '__main__':
#     schedulers = []
#
#     for n in range(200):
#         schedulers.append(Scheduler(safe_to_csv_file, '1m', ticker='TON-USDT', timeframe='1m'))
#     # user1_scheduler.run()
#     print(schedulers)
# user2_scheduler = Scheduler(safe_to_csv_file, '1m', ticker='SOL-USDT', timeframe='1m')
# user2_scheduler.run()


# 50 групп стдудентов
# объект 1 группы (сам список, кол-во человек, дата начало обучения, название группы)
# объект 2 группы (сам список, кол-во человек, дата начало обучения, название группы)

# [объект 1 группы, объект 2 группы]


#
#
# s1 = Scheduler(safe_to_csv_file, '1m', ticker='BTC-USDT', timeframe='1m')
# s2 = Scheduler(safe_to_csv_file, '1m', ticker='SOL-USDT', timeframe='1m')
# s3 = Scheduler(safe_to_csv_file, '5m', ticker='TON-USDT', timeframe='5m')
#
# print(s1._interval, s1._kwargs['ticker'])
# schedulers[f"{s1._kwargs['ticker']}_{s1._interval}"] = s1
# schedulers[f"{s2._kwargs['ticker']}_{s2._interval}"] = s2
# schedulers[f"{s3._kwargs['ticker']}_{s3._interval}"] = s3
# print(scheduler)
#
# scheduler_run = scheduler[f"{s1._kwargs['ticker']}_{s1._interval}"]
# print(scheduler_run)
#
# scheduler_run
# Запускаем все планировщики асинхронно
# run_tasks = []
# for s in schedulers:
#     run_tasks.append(s.run_async())
#
# await asyncio.gather(*run_tasks)

# start_time = time.time()
# schedulers = []
# # Создаем задачи для асинхронного создания экземпляров
# create_tasks = []
# for n in range(2):
#     # Обертка для асинхронного создания
#     task = asyncio.to_thread(Scheduler, safe_to_csv_file, '1m', ticker='TON-USDT', timeframe='1m')
#     create_tasks.append(task)
#
# # Параллельное создание экземпляров
# schedulers = await asyncio.gather(*create_tasks)
# print(len(schedulers))
#
# # Код, время выполнения которого нужно измерить
# end_time = time.time()
# elapsed_time = end_time - start_time
# print(f"Время выполнения: {elapsed_time} секунд")
