import asyncio
from connection_oracle.connection_oracle_db import connection
import pandas as pd
from fastapi.concurrency import run_in_threadpool
import json


async def get_strategies():
    cursor = connection.cursor()
    cursor.execute('select NAME_STRATEGY from T_STRATEGY')
    rows = cursor.fetchall()

    cursor.close()

    return [row[0] for row in rows]


async def get_coins():
    cursor = connection.cursor()
    cursor.execute('select TICKER_CODE from T_TICKERS')
    rows = cursor.fetchall()

    cursor.close()

    return [row[0] for row in rows]


async def get_alarm_times() -> list:
    cursor = connection.cursor()
    cursor.execute('select TIMEFRAME from T_ALARM_TIMES')
    rows = cursor.fetchall()

    cursor.close()

    return [row[0] for row in rows]


async def get_user_id(telegram_id: int):
    cursor = connection.cursor()
    id_value = cursor.callfunc(name='pk_users.get_id_user', return_type=int, parameters=[telegram_id])

    await asyncio.sleep(0)

    cursor.close()
    return id_value


async def get_strategy_id(name_strategy: str):
    cursor = connection.cursor()
    id_value = cursor.callfunc(name='pk_strategy.get_strategy_id', return_type=int, parameters=[name_strategy])

    await asyncio.sleep(0)

    cursor.close()
    return id_value


async def get_ticker_id(name_ticker: str):
    cursor = connection.cursor()
    id_value = cursor.callfunc(name='pk_tickers.get_ticker_id', return_type=int, parameters=[name_ticker])

    await asyncio.sleep(0)

    cursor.close()
    return id_value


async def get_alarm_time_id(alarm_time: str):
    cursor = connection.cursor()
    id_value = cursor.callfunc(name='pk_alarm_times.get_id_alarm_time', return_type=int, parameters=[alarm_time])

    await asyncio.sleep(0)

    cursor.close()
    return id_value


async def data_for_using_strategies(telegram_id: int, name_strategy: str, name_ticker: str, alarm_time: str):
    tasks = [
        get_user_id(telegram_id),
        get_strategy_id(name_strategy),
        get_ticker_id(name_ticker),
        get_alarm_time_id(alarm_time)
    ]

    results = await asyncio.gather(*tasks)
    return results


async def get_user_strategies(telegram_id: int):
    cursor = connection.cursor()
    data = cursor.callfunc(name='pk_using_strategies.get_user_strategies', return_type=str, parameters=[telegram_id])

    await asyncio.sleep(0)

    cursor.close()
    user_strategies = json.loads(data)
    return user_strategies


async def get_id_ticker_and_timeframe(name_ticker: str, alarm_time: str) -> tuple:
    tasks = [
        get_ticker_id(name_ticker),
        get_alarm_time_id(alarm_time)
    ]

    results = await asyncio.gather(*tasks)
    return results


async def get_last_date(name_ticker: str, alarm_time: str):
    results = await get_id_ticker_and_timeframe(name_ticker, alarm_time)
    ticker, timeframe = results

    cursor = connection.cursor()
    last_date = cursor.callfunc(name='pk_okx_data.get_last_date', return_type=str, parameters=[ticker, timeframe])

    await asyncio.sleep(0)

    cursor.close()
    return last_date


async def exists_ticker_and_timeframe(name_ticker: str, alarm_time: str):
    results = await get_id_ticker_and_timeframe(name_ticker, alarm_time)
    ticker, timeframe = results

    cursor = connection.cursor()
    exists = cursor.callfunc(
        name='pk_okx_data.exists_ticker_and_timeframe', return_type=int, parameters=[ticker, timeframe]
    )

    await asyncio.sleep(0)

    cursor.close()
    return exists


async def ticker_and_timeframe_un_use_others(ticker: str, timeframe: str, telegram_id):
    results = await get_id_ticker_and_timeframe(ticker, timeframe)
    ticker_id, timeframe_id = results
    user_id = await get_user_id(telegram_id)

    cursor = connection.cursor()
    exists_data = cursor.callfunc(
        name='pk_using_strategies.ticker_and_timeframe_un_use_others',
        return_type=int,
        parameters=[ticker_id, timeframe_id, user_id]
    )

    await asyncio.sleep(0)

    cursor.close()
    return exists_data


async def choose_user_all_strategies(telegram_id: int):
    user_id = await get_user_id(telegram_id)

    cursor = connection.cursor()
    data = cursor.callfunc(name='pk_using_strategies.choose_user_all_strategies', return_type=str, parameters=[user_id])

    await asyncio.sleep(0)

    cursor.close()
    user_strategies = json.loads(data)
    return user_strategies


async def get_quantity_strategy_user(telegram_id: int):
    cursor = connection.cursor()
    quantity_strategy = cursor.callfunc(
        name='pk_users.get_quantity_strategy', return_type=int, parameters=[telegram_id]
    )

    await asyncio.sleep(0)

    cursor.close()
    return quantity_strategy


async def get_candles_df(engine, ticker, timeframe):
    results = await get_id_ticker_and_timeframe(ticker, timeframe)
    ticker_id, timeframe_id = results
    query = """
        SELECT 
            TIMEFRAME,
            "OPEN",
            HIGH,	
            LOW,	
            "CLOSE"
        FROM T_OKX_DATA
        WHERE TICKER_ID = :ticker_id
          AND ALARM_TIME_ID = :timeframe_id
        ORDER BY TIMEFRAME
    """

    params = {"ticker_id": ticker_id, "timeframe_id": timeframe_id}

    def _load_df():
        return pd.read_sql(query, engine, params=params)

    df = await run_in_threadpool(_load_df)
    return df


async def get_data_for_scheduler(engine):
    query = """
        SELECT DISTINCT
            tt.TICKER_CODE AS ticker,
            tat.TIMEFRAME AS timeframe
        FROM T_USING_STRATEGIES tus
        JOIN T_TICKERS tt      ON tus.TICKER_ID = tt.ID 
        JOIN T_ALARM_TIMES tat ON tus.ALARM_TIME_ID = tat.ID
    """

    def _load():
        df = pd.read_sql(query, engine)
        return list(df.itertuples(index=False, name=None))

    return await run_in_threadpool(_load)


async def get_data_for_stop_scheduler(telegram_id: int):
    user_strategies = await choose_user_all_strategies(telegram_id)

    un_use_data = []

    for strategy in user_strategies:
        ticker = strategy['ticker']
        timeframe = strategy['timeframe']
        exists_data = await ticker_and_timeframe_un_use_others(ticker, timeframe, telegram_id)
        if exists_data:
            un_use_data.append((ticker, timeframe))
    print('Не используемые данные', un_use_data)
    return un_use_data
