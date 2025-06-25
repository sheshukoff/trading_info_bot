import asyncio
from asyncio import Task

from aioconsole import ainput


async def long_running_task():
    try:
        while True:
            await asyncio.sleep(10)
            print("Работаю...10 секунд")
    except asyncio.CancelledError:
        print("Задача отменена")


async def short_running_task():
    try:
        while True:
            await asyncio.sleep(3)
            print("Работаю... 3 секунды")
    except asyncio.CancelledError:
        print("Задача отменена")


async def start_task(available_tasks, active_tasks, key):
    try:
        task_info = available_tasks[key]  # получил название функции
        print(task_info)
        task = asyncio.create_task(task_info())  # Задача
        print(task)
        active_tasks[key] = {'state': True, 'task': task}
        return f"Стратегия {key} запущена"
    except KeyError:
        print(f'Такой стратегии нет {key}')


async def stop_task(active_tasks: dict, key: str) -> str:

    task_info = active_tasks[key]
    task: Task = task_info['task']
    task.cancel()
    task_info['state'] = False
    print(active_tasks)
    await task
    return f"{key} остановлена"


async def main():
    "Функция input пользователь что то вводит"

    available_tasks = {
        'RSI 14': long_running_task,
        'Цены по BTC': short_running_task
    }

    active_tasks = {}  #  можно вместо 'state' использовать метод task.canselled(),
                       #  что показывает включенали задача

    while True:
        try:
            user_input = await ainput("> ")
            print(user_input)

            task_info = active_tasks.get(user_input)
            if not task_info:
                print(task_info)
                await start_task(available_tasks, active_tasks, user_input)
            else:
                if task_info.get('state') is True:
                    await stop_task(active_tasks, user_input)
                else:
                    await start_task(available_tasks, active_tasks, user_input)

        except KeyboardInterrupt:
            print('Exit')


if __name__ == "__main__":
    asyncio.run(main())
