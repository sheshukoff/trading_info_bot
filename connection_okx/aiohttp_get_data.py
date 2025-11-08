import pandas as pd
from datetime import datetime, timedelta
from tzlocal import get_localzone
import asyncio
from aiohttp import ClientSession, ClientResponse
import aiohttp


# --- Глобальная aiohttp сессия ---
SESSION: aiohttp.ClientSession | None = None


async def get_session() -> aiohttp.ClientSession:
    """Возвращает активную aiohttp-сессию или создаёт новую."""
    global SESSION
    if SESSION is None or SESSION.closed:
        SESSION = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100, keepalive_timeout=60)
        )
        print("🌐 Aiohttp session создана")
    return SESSION


async def close_session():
    """Корректно закрывает aiohttp-сессию."""
    global SESSION
    if SESSION and not SESSION.closed:
        await SESSION.close()
        print("🧹 Aiohttp session закрыта")


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


async def extrac_local_data(inst_id: str, bar: str, data_time: str, session: ClientSession, limit=100) -> ClientResponse:
    endpoint = '/api/v5/market/candles'
    params = {
        'instId': inst_id,
        'bar': bar,
        'before': data_time,
        'limit': limit
    }

    url = 'https://www.okx.com' + endpoint
    async with session.get(url, params=params) as response:
        data = await response.json()
        return data['data']


async def extract_history_data(inst_id: str, bar: str, limit=100) -> ClientResponse:
    session = await get_session()
    endpoint = '/api/v5/market/candles'
    params = {
        'instId': inst_id,
        'bar': bar,
        'limit': limit,
    }

    url = 'https://www.okx.com' + endpoint
    async with session.get(url, params=params) as response:
        data = await response.json()
        return data['data']


async def processing_data(data) -> pd.DataFrame:
    columns = ['ts', 'open', 'high', 'lowest', 'close', 'volume', 'volCcy', 'volCcyQuote', 'confirm']
    df = pd.DataFrame(data, columns=columns)

    df['ts'] = pd.to_datetime(pd.to_numeric(df['ts']), unit="ms") + pd.Timedelta(hours=await get_local_tz())

    df = await change_type_data(df)
    df.sort_values(by='ts', inplace=True)

    return df.head(-1)


async def change_type_data(df):
    df = df.astype({
        'open': 'float64',
        'high': 'float64',
        'lowest': 'float64',
        'close': 'float64',
        'volume': 'float64',
        'volCcy': 'float64',
        'volCcyQuote': 'float64',
        'confirm': 'int8'
    })
    return df


async def get_local_data_okx(coin, timeframe, new_date):
    # new_date = str(int(datetime.strptime(df['ts'].iloc[-1], '%Y-%m-%d %H:%M:%S').timestamp() * 1000))
    response = await extrac_local_data(coin, timeframe, new_date, session)
    df = await processing_data(response)  # Добавление новых данных в бд
    return df, coin, timeframe


async def get_history_data_okx(coin, timeframe):
    response = await extract_history_data(coin, timeframe)
    df = await processing_data(response)
    return df, coin, timeframe


async def main():
    await get_history_data_okx('BTC-USDT', '1m')

if __name__ == '__main__':
    asyncio.run(main())
