import schedule
import time
from connection_okx.get_data import processing_data, safe_to_csv_file

times_every_minutes = [f"{h:02d}:{m:02d}:00" for h in range(24) for m in range(60)]


def job():
    print("I'm working...")


def scheduler_work_every_minutes(work_times: list, ticker: str, timeframe: str):
    for work_time in work_times:
        schedule.every().day.at(work_time).do(safe_to_csv_file, ticker=ticker, timeframe=timeframe)


scheduler_work_every_minutes(times_every_minutes, 'BTC-USDT', '1m')



# work_hours = ['03:00', '07:00', '11:00', '15:00', '19:00', '23:00']
#
# for work_hour in work_hours:
#     schedule.every().day.at(work_hour).do(job)



# work_hours = ['11:36:00', '11:37:00', '11:38:00', '11:39:00']

# for work_hour in work_hours:
#     result = schedule.every().day.at(work_hour).do(processing_data, ticker='BTC-USDT', timeframe='1m')
#     print(result)
    # schedule.every().day.at(work_hour).do(job)

    # schedule.every().minutes.do(job)
    # schedule.every(15).seconds.do(job)


while True:
    schedule.run_pending()
    time.sleep(1)


# сгенерировать для теста каждую минуту запускать, какую то работу job()
# написать функцию, которая вызовет внешнюю
# в core я должен import from scheduler.py и вызвать из scheduler.py функцию
# пока сделать сохранения файла например каждую минуту

# функция safe_data будет сохранять данные .csv - простой вариант
# функция send_dataframe будет передавать dataframe в очередь rabbit_mq - то как должно быть
