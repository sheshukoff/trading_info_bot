import schedule
import time


class Scheduler:
    # Атрибуты
    ALARM_TIMES = {
        '1m': [f"{h:02d}:{m:02d}:00" for h in range(24) for m in range(60)],
        '5m': [f"{h:02d}:{m:02d}:00" for h in range(24) for m in range(0, 60, 5)],
        '15m': [f"{h:02d}:{m:02d}:00" for h in range(24) for m in range(0, 60, 15)],
        '30m': [f"{h:02d}:{m:02d}:00" for h in range(24) for m in range(0, 60, 30)],
        '1H': [f"{h:02d}:00:00" for h in range(24)],
        '4H': [f'{h:02d}:00:00' for h in range(3, 24, 4)],
        '1D': ['03:00:00']
    }

    # Конструктор
    def __init__(self, function, interval, **kwargs):
        try:
            times = self.ALARM_TIMES[interval]
            print(f'Работаю по интевалу {interval}')
            if times:
                for work_time in times:
                    schedule.every().day.at(work_time).do(lambda: function(**kwargs))
        except KeyError:
            print(f'Такого таймфрейма нет: {interval}')

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print('exit')


# def one_plus_two(a, b):
#     print(a + b)
#     return a + b


# scheduler = Scheduler(one_plus_two, '1m', a=4, b=7)


# def scheduler(function, interval, **kwargs):
#     try:
#         times = ALARM_TIMES[interval]
#
#         if times:
#             for work_time in times:
#                 schedule.every().day.at(work_time).do(lambda: function(**kwargs))
#     except KeyError:
#         print(f'Такого таймфрейма нет: {interval}')


if __name__ == '__main__':
    def one_plus_two(a, b):
        print(a + b)
        return a + b


    scheduler = Scheduler(one_plus_two, '1m', a=4, b=7)
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
