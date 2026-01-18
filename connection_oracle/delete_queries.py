import oracledb
from connection_oracle.connection_oracle_db import connection
from connection_oracle.get_queries import data_for_using_strategies, get_user_id


async def delete_user(p_telegram_id: int) -> int:
    cursor = connection.cursor()
    count_row = cursor.callfunc(name='pk_users.delete_user', return_type=int, parameters=[p_telegram_id])

    connection.commit()
    cursor.close()

    return count_row


async def delete_user_strategy(telegram_id: int, strategy: str, ticker: str, alarm_time: str):
    results = await data_for_using_strategies(telegram_id, strategy, ticker, alarm_time)
    user_id, strategy_id, ticker_id, alarm_time_id = results
    print(results)
    cursor = connection.cursor()
    try:
        id_value = cursor.callfunc(
            name='pk_using_strategies.delete_user_strategy',
            return_type=int,
            parameters=[user_id, strategy_id, ticker_id, alarm_time_id]
        )

        connection.commit()
        cursor.close()

        return id_value
    except oracledb.IntegrityError as error:
        error, = error.args

        if error.code == 1403:  # ORA-01403
            print("Такой стратегии у пользователя нет")


async def delete_user_all_strategies(telegram_id: int):
    user_id = await get_user_id(telegram_id)

    cursor = connection.cursor()
    try:
        delete_rows = cursor.callfunc(
            name='pk_using_strategies.delete_user_all_strategies',
            return_type=int,
            parameters=[user_id]
        )

        connection.commit()
        cursor.close()

        return delete_rows
    except oracledb.IntegrityError as error:
        error, = error.args

        if error.code == 1403:  # ORA-01403
            print("Такой стратегии у пользователя нет")
