import requests
import pandas as pd
from datetime import datetime, timedelta
from tzlocal import get_localzone
import asyncio


async def get_local_tz() -> int:
    local_tz = get_localzone()
    now = datetime.now(local_tz)

    await asyncio.sleep(0.05)

    offset_sec = now.utcoffset().total_seconds()
    offset_hours = offset_sec / 3600

    return int(offset_hours)


async def date_two_years_ago() -> int:
    now = datetime.now()
    eight_month_ago = now - timedelta(days=365 * 2)
    return int(eight_month_ago.replace(microsecond=0).timestamp() * 1000)


async def now_date() -> int:
    now = datetime.now()
    return int(now.replace(microsecond=0).timestamp() * 1000)


async def extrac_local_data(inst_id: str, bar: str, limit: int) -> requests.models.Response:
    endpoint = '/api/v5/market/candles'
    params = {
        'instId': inst_id,
        'bar': bar,
        'limit': limit,
    }

    url = 'https://www.okx.com' + endpoint
    response = requests.get(url, params=params)
    return response


async def processing_data(ticker: str, timeframe: str, limit=300) -> pd.DataFrame:
    result = await extrac_local_data(ticker, timeframe, limit)
    result = result.json()['data']

    columns = ['ts', 'open', 'high', 'lowest', 'close', 'volume', 'volCcy', 'volCcyQuote', 'confirm']
    df = pd.DataFrame(result, columns=columns)

    df['ts'] = pd.to_datetime(pd.to_numeric(df['ts']), unit="ms") + pd.Timedelta(hours=await get_local_tz())

    await asyncio.sleep(0.05)

    df = await change_type_data(df)
    df.sort_values(by='ts', inplace=True)

    return df.head(-1)


async def change_type_data(df):
    df['open'] = df['open'].astype('float64')
    df['high'] = df['high'].astype('float64')
    df['lowest'] = df['lowest'].astype('float64')
    df['close'] = df['close'].astype('float64')
    df['volume'] = df['volume'].astype('float64')
    df['volCcy'] = df['volCcy'].astype('float64')
    df['volCcyQuote'] = df['volCcyQuote'].astype('float64')
    df['confirm'] = df['confirm'].astype('int8')

    return df


async def get_data_okx(ticker: str, timeframe: str):
    df = await processing_data(ticker, timeframe)
    return df, ticker


async def main():
    await get_data_okx('BTC-USDT', '1m')


if __name__ == '__main__':
    asyncio.run(main())
