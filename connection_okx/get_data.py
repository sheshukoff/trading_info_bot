import requests
import pandas as pd
from datetime import datetime, date, timedelta
from tzlocal import get_localzone


def get_local_tz() -> int:
    local_tz = get_localzone()
    now = datetime.now(local_tz)

    offset_sec = now.utcoffset().total_seconds()
    offset_hours = offset_sec / 3600

    return int(offset_hours)


def date_eight_month_ago() -> int:
    hours_back = 1440 * 4
    now = datetime.now()
    eight_month_ago = now - timedelta(hours=hours_back - 4)
    return int(eight_month_ago.replace(microsecond=0).timestamp() * 1000)


def now_date() -> int:
    now = datetime.now()
    return int(now.replace(microsecond=0).timestamp() * 1000)


start_date = date_eight_month_ago()
end_date = now_date()
print('старт', start_date, 'конец', end_date)

print(4 * 3600 * 1000 * 300)


while start_date < end_date:
    start_date += 4 * 3600 * 1000 * 300

    if start_date > end_date:
        print('конец', end_date)
    print('старт', start_date)

# print(int(date_two_years_ago().timestamp() * 1000), date_two_years_ago())
# def get_history_candles(inst_id='BTC-USDT', bar='4H', limit=100):
#     endpoint = '/api/v5/market/history-candles'
#     params = {
#         'instId': inst_id,
#         'bar': bar,
#         'limit': limit
#     }
#
#     url = 'https://www.okx.com' + endpoint
#     response = requests.get(url)
#
#     all_tickers = []
#     print(response.json())
#
#     # for ticker in response.json()['data']:
#     #     all_tickers.append(ticker['instId'])
#     #
#     # return all_tickers
#
#
# get_history_candles()

# start_date = int(date_two_years_ago().timestamp() * 1000
# print(str(int(start_date.timestamp() * 1000)))
# end_date =
#
#
#
# endpoint = '/api/v5/market/candles'
# params = {
#     'instId': 'BTC-USDT',
#     'bar': '4H',  # 1-day candles
#     'limit': '300',  # Last 100 days
#     'after': '1749560050000'
# }
#
# url = 'https://www.okx.com' + endpoint
# response = requests.get(url, params=params)
# print(response.json())
# #
# df = pd.DataFrame(response.json()['data'])
#
# columns = ['ts', 'open', 'high', 'lowest', 'close', 'volume', 'volCcy', 'volCcyQuote', 'confirm']
#
# df.columns = columns
# print(df)
#
# df['ts'] = pd.to_datetime(df['ts'], unit='ms') + pd.Timedelta(hours=get_local_tz())
# print(df)
