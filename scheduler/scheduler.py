import asyncio
import schedule
from functools import partial


class Scheduler:
    __ALARM_TIMES = {
        '1m': [f"{__h:02d}:{__m:02d}:00" for __h in range(24) for __m in range(60)],
        '5m': [f"{__h:02d}:{__m:02d}:00" for __h in range(24) for __m in range(0, 60, 5)],
        '15m': [f"{__h:02d}:{__m:02d}:00" for __h in range(24) for __m in range(0, 60, 15)],
        '30m': [f"{__h:02d}:{__m:02d}:00" for __h in range(24) for __m in range(0, 60, 30)],
        '1H': [f"{__h:02d}:00:00" for __h in range(24)],
        '4H': [f'{__h:02d}:00:00' for __h in range(3, 24, 4)],
        '1D': ['03:00:00']
    }

    def __init__(self, function, interval, **kwargs):
        self.__function = function
        self._interval = interval
        self._kwargs = kwargs

    @classmethod
    async def create(cls, function, interval, **kwargs):
        self = cls(function, interval, **kwargs)
        await self.__setup_alarm_times()
        return self

    async def __setup_alarm_times(self):
        try:
            times = self.__ALARM_TIMES[self._interval]
            for work_time in times:
                job = partial(self.__function, **self._kwargs)
                schedule.every().day.at(work_time).do(job)
        except KeyError:
            print(f'❌ Такого таймфрейма нет: {self._interval}')

    async def run_async(self):
        try:
            while True:
                schedule.run_pending()
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("Scheduler task cancelled")

# if __name__ == '__main__':
#     def one_plus_two(a, b):
#         print(a + b)
#         return a + b
#
#
#     scheduler = Scheduler(one_plus_two, '1m', a=7, b=5)
#     asyncio.gather(scheduler.run_async())
#     asyncio.run()
# try:
#     while True:
#         schedule.run_pending()
#         time.sleep(1)
# except KeyboardInterrupt:
#     print('exit')

# сгенерировать для теста каждую минуту запускать, какую то работу job()
# написать функцию, которая вызовет внешнюю
# в core я должен import from scheduler.py и вызвать из scheduler.py функцию
# пока сделать сохранения файла например каждую минуту

# функция safe_data будет сохранять данные .csv - простой вариант
# функция send_dataframe будет передавать dataframe в очередь rabbit_mq - то как должно быть

# Возможен еще один вариант scheduler достает данные за какой то период (сейчас не важно)
# и после того как он достанет данные можно наложить индикаторы на данные и затем сохранять их пока в csv file

# Сейчас нужно проверить сколько времени нужно для извлечения данных, наложение индикаторов и полчение сигнала:


# Нужно написать универсальную функцию для генерации списка будильников в разными интевалами


# При сбоях в работе планировщика, будет следующая проблема, будет прислано столько собщений,
# сколько было заведено будильников (пометка возможной проблемы)

# Домашнее задание
# + Откатить обратно commit до самого свежего
# + Пробежать дебагером по class Scheduler (Обратить внимание на появления переменных)

# Отмечать + что сделано

# посмотреть про классы с асинхронно
# + посмотреть бублиотеку планировщика который будет асинхронным APScheduler, aiojobs, aiocron
# + посмотреть время использования кода (измерить время) профилирование кода
# Доп вопросы:
#   Один пользователь может создать например:
#       Все 7 tieframe'ов и 10 монет - это будет 70 объектов класса?


# BTC 4H 1D
# SOL 4H 1D
# TON 4H 1D

# Первый тип планировщиков должен просто извлекать данные и записывать
# Должна быть проверка проверка комбинации (Валюнтной пары и таймфрейма)
#
#
# Второй тип планировщиков должен наложить индикаторы и сообщить есть ли сигнал
# Нужно понять кому расслылать сигналы
#
#


# какая то планировщик ждет фуру +-
# какая то планировщик принимает товар --
# до пех пор пока какой то планировщик не раскложит на ячейки ---


# TODO следующим улучшение сделать класс MenagerSchedulers