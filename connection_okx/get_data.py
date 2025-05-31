import requests
import pandas as pd
from datetime import datetime
from tzlocal import get_localzone


def get_local_tz() -> int:
    local_tz = get_localzone()
    now = datetime.now(local_tz)

    offset_sec = now.utcoffset().total_seconds()
    offset_hours = offset_sec / 3600

    return int(offset_hours)


print(get_local_tz())

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


# endpoint = '/api/v5/market/candles'
# params = {
#     'instId': 'BTC-USDT',
#     'bar': '4H',  # 1-day candles
#     'limit': '100'  # Last 100 days
# }
#
# url = 'https://www.okx.com' + endpoint
# response = requests.get(url, params=params)
# print(response.json())
#
# df = pd.DataFrame(response.json()['data'])
#
# columns = ['ts', 'open', 'high', 'lowest', 'close', 'volume', 'volCcy', 'volCcyQuote', 'confirm']
#
# df.columns = columns
#
# df['ts'] = pd.to_datetime(df['ts'], unit='ms') + pd.Timedelta(hours=3)
# print(df)

