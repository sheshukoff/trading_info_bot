import asyncio
from asyncio import Task

from aioconsole import ainput


# async def ask_name():
#     try:
#         while True:
#             name = await ainput("Напишите что хотите: ")
#             print(f"Привет, вы выбрали {name}!")
#             await asyncio.sleep(5)
#             yield name
#     except asyncio.CancelledError:
#         print("Задача отменена")


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
    task_info = available_tasks[key]  # получил название функции
    print(task_info)
    task = asyncio.create_task(task_info())  # Задача
    print(task)
    active_tasks[key] = {'state': True, 'task': task}
    return f"Стратегия {key} запущена"


async def stop_task(available_tasks, active_tasks: dict[dict[bool, Task]], key):
    # task_info = available_tasks[key]  # TODO проверка с основным справочником
    # print('task_info', task_info)
    task_info = active_tasks[key]
    task: Task = task_info['task']
    task.cancel()
    task_info['state'] = False
    print(active_tasks)
    await task
    return f"{key} остановлена"


async def handle_command():
    pass


async def main():
    "Функция input пользователь что то вводит"

    available_tasks = {
        'RSI 14': long_running_task,
        'Цены по BTC': short_running_task
    }

    active_tasks = {}  # TODO можно вместо 'state' использовать метод task.canselled(),
                       # TODO что показывает включенали задача

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
                    await stop_task(available_tasks, active_tasks, user_input)
                else:
                    await start_task(available_tasks, active_tasks, user_input)

                # if task_info.get('state') is True:
                #     result = await stop_task(available_tasks, active_tasks, user_input)
                #     print(result)
                # else:
                #     result = await start_task(available_tasks, active_tasks, user_input)
                #     print(result)
        except KeyboardInterrupt:
            print('Exit')






        # new_task = asyncio.create_task(available_tasks[user_input]())  # RSI 14
        # print(new_task)

    # async for answer in ask_name():
    #     # answer = await ask_name()
    #
    #     current_task = None
    #     new_task = asyncio.create_task(dictionary_1[answer]())
    #     print(answer)
    #     current_task = new_task
    #
    #     if current_task != new_task:
    #         current_task.cancel()

    # while True:
    #     if current_task is None:
    #         new_task = asyncio.create_task(dictionary_1[answer]())  # RSI 14
    #         current_task = new_task
    #
    #     if current_task != new_task:
    #         current_task.cancel()
    #         try:
    #             await current_task
    #         except asyncio.CancelledError:
    #             print(f'Задача успешно отменена {answer}')
    # else:
    #     current_task.cancel()
    #     print("Задача успешно отменена")

    # if current_task != new_task:
    #     new_task = asyncio.create_task(dictionary_1[answer]())
    #     current_task.cancel()
    #     current_task = new_task
    #     # print(current_task)
    # else:
    #     current_task.cancel()
    # try:
    #     await current_task
    # except asyncio.CancelledError:
    #     print("Задача успешно отменена")

    # elif 'Цены BTC':
    #     task = asyncio.create_task(short_running_task())
    #
    # answer.cancel()
    #     print(current_task)
    #     try:
    #         await current_task
    #     except asyncio.CancelledError:
    #         print("Задача успешно отменена")


if __name__ == "__main__":
    asyncio.run(main())

# strategy = {'RSI 14': long_running_task,
#             'Цены по BTC': short_running_task}
#
# active_strategy = {}
#
#
# while True:
#     try:
#         user_input = input('Напиши стратегию:  ')
#
#         if active_strategy.get(user_input) is True:
#             print(f'Отключаю стратегию {user_input}')
#             active_strategy[user_input] = False
#
#         else:
#             active_strategy[user_input] = True
#             print(f'Стратегия подключена {user_input}')
#     except KeyboardInterrupt:
#         print('Exit')
# import asyncio
#
# async def long_running_task():
#     try:
#         while True:
#             await asyncio.sleep(10)
#             print("Работаю...10 секунд")
#     except asyncio.CancelledError:
#         print("Задача long_running_task отменена")
#
#
# async def short_running_task():
#     try:
#         while True:
#             await asyncio.sleep(3)
#             print("Работаю...3 секунды")
#     except asyncio.CancelledError:
#         print("Задача short_running_task отменена")
#
# # Словарь доступных стратегий
# dictionary_1 = {
#     'RSI 14': long_running_task,
#     'Цены по BTC': short_running_task
# }
#
#
# async def main():
#     current_task = None
#     loop = asyncio.get_event_loop()
#
#     while True:
#         # Ввод пользователя (не блокирует asyncio)
#         name = await loop.run_in_executor(None, input, "\nВведите стратегию (или 'стоп'): ")
#
#         if name.lower() == "стоп":
#             print("Завершаем программу...")
#             if current_task:
#                 current_task.cancel()
#                 try:
#                     await current_task
#                 except asyncio.CancelledError:
#                     pass
#             break
#
#         if name in dictionary_1:
#             # Отменяем текущую задачу
#             if current_task:
#                 print("⛔ Отменяем текущую стратегию...")
#                 current_task.cancel()
#                 try:
#                     await current_task
#                 except asyncio.CancelledError:
#                     print("✅ Отменена")
#
#             # Запускаем новую
#             print(f"🚀 Запуск стратегии: {name}")
#             current_task = asyncio.create_task(dictionary_1[name]())
#         else:
#             print("❓ Неизвестная стратегия. Доступные:", ", ".join(dictionary_1.keys()))
#
# # Запуск
# if __name__ == "__main__":
#     asyncio.run(main())
