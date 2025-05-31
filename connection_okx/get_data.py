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


def date_two_years_ago() -> int:
    now = datetime.now()
    eight_month_ago = now - timedelta(days=365 * 2)
    return int(eight_month_ago.replace(microsecond=0).timestamp() * 1000)


def now_date() -> int:
    now = datetime.now()
    return int(now.replace(microsecond=0).timestamp() * 1000)


def extrac_history_data(inst_id, bar, limit, start_date):
    endpoint = '/api/v5/market/history-candles'
    params = {
        'instId': inst_id,
        'bar': bar,
        'limit': limit,
        'after': str(start_date)
    }

    url = 'https://www.okx.com' + endpoint
    response = requests.get(url, params=params)
    return response


def extrac_local_data(inst_id, bar, limit, start_date):
    endpoint = '/api/v5/market/history-candles'
    params = {
        'instId': inst_id,
        'bar': bar,
        'limit': limit,
        'before': str(start_date)
    }

    url = 'https://www.okx.com' + endpoint
    response = requests.get(url, params=params)
    return response


def test() -> pd.DataFrame:
    days = 4 * 3600 * 1000 * 100
    start_date = date_two_years_ago()
    end_date = now_date()
    df = pd.DataFrame()

    while True:
        start_date += days

        if start_date < end_date:
            print('старт', datetime.fromtimestamp(start_date / 1000))
            data = extrac_history_data('BTC-USDT', '4H', 100, start_date)
            df = pd.concat([pd.DataFrame(data.json()['data']), df], axis=0, ignore_index=True)
        else:
            break

    return df


def test2() -> pd.DataFrame:
    df = pd.read_csv('BTC-USDT.csv')
    first_date = pd.to_datetime(df.loc[0, 'ts'])
    start_date = int(first_date.timestamp() * 1000)
    print(start_date)
    df = pd.DataFrame()

    data = extrac_local_data('BTC-USDT', '4H', 300, start_date)
    df = pd.concat([pd.DataFrame(data.json()['data']), df], axis=0, ignore_index=True)

    return df


columns = ['ts', 'open', 'high', 'lowest', 'close', 'volume', 'volCcy', 'volCcyQuote', 'confirm']
df = test2()
df = df.set_axis(columns, axis='columns')

df['ts'] = pd.to_datetime(df['ts'], unit='ms') + pd.Timedelta(hours=get_local_tz())
print(df)
print(df['ts'].is_monotonic_decreasing)

df2 = pd.read_csv('BTC-USDT.csv')

df3 = pd.concat([df, df2], axis=0, ignore_index=True)

print(df3.columns)
df3['ts'] = pd.to_datetime(df3['ts'])
print(df3['ts'].is_monotonic_decreasing)

# df = pd.read_csv('BTC-USDT.csv')
#
# # df['ts'] = pd.to_datetime(df['ts'], unit='ms') + pd.Timedelta(hours=get_local_tz())
# print(df['open'].min(), df['open'].max())
# print()
# print(df.sort_values(by='ts', ascending=True)['ts'].is_monotonic_increasing, 'монотонно возрастает')
# # print(df['ts'].value_counts().head(30))
# print(df)
