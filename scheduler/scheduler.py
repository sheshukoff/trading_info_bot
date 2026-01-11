import asyncio
from typing import Dict
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.job import Job


class DynamicSchedulerManager:
    __ALARM_TIMES = {
        '1m': {'second': 5},
        '5m': {'minute': '*/5', 'second': 5},
        '15m': {'minute': '*/15', 'second': 5},
        '30m': {'minute': '*/30', 'second': 5},
        '1H': {'minute': 0, 'second': 5},
        '4H': {'hour': '3-23/4', 'minute': 0, 'second': 5},
        '6H': {'hour': '3-23/6', 'minute': 0, 'second': 5},
        '12H': {'hour': '3-23/12', 'minute': 0, 'second': 5},
        '1D': {'hour': 3, 'minute': 0, 'second': 5},
    }

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs: Dict[str, Job] = {}
        self.job_counter = 0

    async def start(self):
        """Запуск планировщика"""
        self.scheduler.start()
        print("Dynamic Scheduler Manager запущен")

        # Запускаем фоновую задачу для поддержания работы
        asyncio.create_task(self._keep_alive())

    async def _keep_alive(self):
        """Фоновая задача для поддержания работы"""
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await self.stop()

    def get_alarm_times(self, timeframe: str):
        try:
            cron_kwargs = self.__ALARM_TIMES.get(timeframe)
            return cron_kwargs
        except KeyError as e:
            print(e)

    def add_job(self, load_function, ticker, timeframe):
        job_id = f'{ticker} {timeframe}'

        try:
            if job_id in self.jobs:
                print(f"Задание с ID '{job_id}' уже существует")
                return False

            cron_kwargs = self.get_alarm_times(timeframe)
            trigger = CronTrigger(**cron_kwargs)

            job = self.scheduler.add_job(
                func=load_function,
                trigger=trigger,
                args=[ticker, timeframe],
                id=job_id,
                replace_existing=False
            )

            self.jobs[job_id] = job
            print(f"Задание '{job_id}' добавлено с расписанием: {trigger}")
            return True

        except Exception as e:
            print(f"Ошибка при добавлении задания '{job_id}': {e}")
            return False

    def remove_job(self, job_id: str) -> bool:
        """Удаление задания"""
        try:
            if job_id not in self.jobs:
                print(f"Задание с ID '{job_id}' не найдено")
                return False

            self.scheduler.remove_job(job_id)
            del self.jobs[job_id]
            print(f"Задание '{job_id}' удалено")
            return True

        except Exception as e:
            print(f"Ошибка при удалении задания '{job_id}': {e}")
            return False

    def change_load_function(self, new_load_function, ticker, timeframe) -> bool:
        """Обновление расписания существующего задания"""
        job_id = f'{ticker} {timeframe}'
        print(self.jobs)
        if job_id not in self.jobs:
            print(f"Задание с ID '{job_id}' не найдено")
            return False
        else:
            self.scheduler.remove_job(job_id)
            print(self.jobs)

        try:
            cron_kwargs = self.get_alarm_times(timeframe)
            trigger = CronTrigger(**cron_kwargs)

            job = self.scheduler.add_job(
                func=new_load_function,
                trigger=trigger,
                args=[ticker, timeframe],
                id=job_id,
                replace_existing=True
            )

            self.jobs[job_id] = job
            print(f"Функция задания '{job_id}' обновлена на {new_load_function}")
            return True
        except Exception as e:
            print(f"Ошибка при обновлении задания '{job_id}': {e}")
            return False

    def stop(self):
        """Остановка менеджера"""
        self.scheduler.shutdown()
        print("Dynamic Scheduler Manager остановлен")
