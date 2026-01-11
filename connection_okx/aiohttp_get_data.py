import pandas as pd
from datetime import datetime, timedelta
from tzlocal import get_localzone
import asyncio
from aiohttp import ClientResponse
import aiohttp
from connection_oracle.get_queries import get_last_date, exists_ticker_and_timeframe, get_candles_df
from connection_oracle.insert_queries import insert_okx_data
from connection_oracle.connection_oracle_db import engine
from strategies.strategies import AVAILABLE_STRATEGIES


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


async def extrac_local_data(inst_id: str, bar: str, data_time: str, limit=100) -> ClientResponse:
    session = await get_session()
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
    columns = ['TIMEFRAME',	'OPEN',	'HIGH', 'LOW', 'CLOSE',	'VOLUME', 'VOL_CCY', 'VOL_CCY_QUOTE', 'CONFIRM']
    df = pd.DataFrame(data, columns=columns)

    df['TIMEFRAME'] = pd.to_datetime(pd.to_numeric(df['TIMEFRAME']), unit="ms") + pd.Timedelta(hours=await get_local_tz())

    df = await change_type_data(df)
    df.sort_values(by='TIMEFRAME', inplace=True)

    return df.head(-1)


async def change_type_data(df):
    df = df.astype({
        'OPEN': 'float64',
        'HIGH': 'float64',
        'LOW': 'float64',
        'CLOSE': 'float64',
        'VOLUME': 'float64',
        'VOL_CCY': 'float64',
        'VOL_CCY_QUOTE': 'float64',
        'CONFIRM': 'int8'
    })
    return df


async def get_local_data_okx(coin, timeframe):
    last_date = await get_last_date(coin, timeframe)
    new_date = str(int(datetime.strptime(last_date, '%Y-%m-%d %H:%M:%S').timestamp() * 1000))
    print(last_date, new_date)
    response = await extrac_local_data(coin, timeframe, new_date)
    df = await processing_data(response)  # Добавление новых данных в бд
    print(df)
    return df, coin, timeframe


async def get_history_data_okx(coin, timeframe):
    response = await extract_history_data(coin, timeframe)
    df = await processing_data(response)
    print(df)
    return df, coin, timeframe


async def get_data_okx(coin, timeframe):
    if await exists_ticker_and_timeframe(coin, timeframe):
        df, coin, timeframe = await get_local_data_okx(coin, timeframe)

        await insert_okx_data(df, engine, coin, timeframe)
        return df, coin, timeframe

    df, coin, timeframe = await get_history_data_okx(coin, timeframe)
    await insert_okx_data(df, engine, coin, timeframe)

    return df, coin, timeframe


async def process_market_data(engine, coin, timeframe):
    await get_data_okx(coin, timeframe)

    df = await get_candles_df(engine, coin, timeframe)
    print(df)
    if df.empty:
        return

    for strategy in AVAILABLE_STRATEGIES:
        print(strategy)
        try:
            await strategy(df, coin, timeframe)
        except Exception as e:
            print(e)


async def main():
    # await get_history_data_okx('BTC-USDT', '1m')
    await get_data_okx('BTC-USDT', '1m')


if __name__ == '__main__':
    asyncio.run(main())