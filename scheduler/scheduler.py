import schedule
import time
from connection_okx.get_data import processing_data, safe_to_csv_file

times_every_minutes = [f"{h:02d}:{m:02d}:00" for h in range(24) for m in range(60)]
times_every_four_hour = [f'{h:02d}:00:00' for h in range(3, 24, 4)]
time_once_day = '03:00:00'


def job():
    print("I'm working...")


def scheduler_work_every_minutes(work_times: list, ticker: str, timeframe: str):
    for work_time in work_times:
        schedule.every().day.at(work_time).do(safe_to_csv_file, ticker=ticker, timeframe=timeframe)


def scheduler_work_every_four_hour(work_times: list, ticker: str, timeframe: str):
    for work_time in work_times:
        schedule.every().day.at(work_time).do(safe_to_csv_file, ticker=ticker, timeframe=timeframe)


def scheduler_work_once_day(work_time: str, ticker: str, timeframe: str):
    print(work_time)
    schedule.every().day.at(work_time).do(safe_to_csv_file, ticker=ticker, timeframe=timeframe)


scheduler_work_every_minutes(times_every_minutes, 'BTC-USDT', '1m')
# scheduler_work_every_minutes(times_every_four_hour, 'BTC-USDT', '4H')
# scheduler_work_once_day(time_once_day, 'BTC-USDT', '1D')


while True:
    schedule.run_pending()
    time.sleep(1)


# сгенерировать для теста каждую минуту запускать, какую то работу job()
# написать функцию, которая вызовет внешнюю
# в core я должен import from scheduler.py и вызвать из scheduler.py функцию
# пока сделать сохранения файла например каждую минуту

# функция safe_data будет сохранять данные .csv - простой вариант
# функция send_dataframe будет передавать dataframe в очередь rabbit_mq - то как должно быть

# Возможен еще один вариант scheduler достает данные за какой то период (сейчас не важно)
# и после того как он достанет данные можно наложить индикаторы на данные и затем сохранять их пока в csv file

# Сейчас нужно проверить сколько времени нужно для извлечения данных, наложение индикаторов и полчение сигнала:


