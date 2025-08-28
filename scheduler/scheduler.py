import asyncio
import schedule


def wrap_async_func(load_function, strategy_functions, **kwargs):
    async def runner():
        # 1. сначала загружаем данные
        data = await load_function(**kwargs)

        # 2. прокидываем в стратегию
        for strategy in strategy_functions:
            try:
                await strategy(data)
            except Exception as e:
                print(f"⚠️ Ошибка в стратегии {strategy.__name__}: {e}")

    def wrapper():
        asyncio.create_task(runner())

    return wrapper


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

    def __init__(self, load_function, strategy_function, interval, **kwargs):
        self._load_function = load_function
        self._strategy_functions = [strategy_function]
        self._interval = interval
        self._kwargs = kwargs

    @classmethod
    async def create(cls, load_function, strategy_function, interval, **kwargs):
        self = cls(load_function, strategy_function, interval, **kwargs)
        await self.__setup_alarm_times()
        return self

    async def __setup_alarm_times(self):
        try:
            times = self.__ALARM_TIMES[self._interval]
            for work_time in times:
                job = wrap_async_func(self._load_function, self._strategy_functions, **self._kwargs)
                schedule.every().day.at(work_time).do(job)
        except KeyError:
            print(f'❌ Такого таймфрейма нет: {self._interval}')

    async def add_strategy(self, strategy):
        self._strategy_functions.append(strategy)

    async def run_async(self):
        try:
            while True:
                schedule.run_pending()
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("Scheduler task cancelled")
