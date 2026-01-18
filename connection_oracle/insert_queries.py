import asyncio
import pandas as pd
import oracledb
from connection_oracle.connection_oracle_db import connection
from connection_oracle.get_queries import get_id_ticker_and_timeframe, data_for_using_strategies


async def insert_using_strategy(telegram_id: int, strategy: str, ticker: str, alarm_time: str):
    results = await data_for_using_strategies(telegram_id, strategy, ticker, alarm_time)
    user_id, strategy_id, ticker_id, alarm_time_id = results
    print(results)
    cursor = connection.cursor()
    try:
        id_value = cursor.callfunc(
            name='pk_using_strategies.add_new_strategy',
            return_type=int,
            parameters=[user_id, strategy_id, ticker_id, alarm_time_id]
        )

        connection.commit()
        cursor.close()

        return id_value
    except oracledb.IntegrityError as error:
        error, = error.args

        if error.code == 1:
            print("Такая стратегия уже подключена пользователем")


async def insert_user(p_telegram_id: int, p_telegram_name: str) -> int:
    cursor = connection.cursor()
    id_value = cursor.callfunc(name='pk_users.add_user', return_type=int, parameters=[p_telegram_id, p_telegram_name])

    await asyncio.sleep(0.1)

    connection.commit()
    cursor.close()

    return id_value


async def insert_okx_data(df: pd.DataFrame, engine, name_ticker: str, alarm_time: str):
    results = await get_id_ticker_and_timeframe(name_ticker, alarm_time)
    ticker_id, timeframe_id = results

    df.insert(0, 'ALARM_TIME_ID', timeframe_id)
    df.insert(0, 'TICKER_ID', ticker_id)

    await asyncio.sleep(0.1)
    df.to_sql(name="t_okx_data", con=engine, if_exists="append", index=False)
