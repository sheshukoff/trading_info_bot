from connection_oracle.queries_to_oracle import get_coins, get_alarm_times


async def get_strategies_data(dialog_manager, **kwargs):
    return {
        "strategies": ['RSI 14', 'EMA/WMA']  # (name, id) # TODO будет из бд ORACLE
    }


async def get_coins_data(dialog_manager, **kwargs):
    coins = await get_coins()
    print(coins)
    return {"coins": coins}


async def get_alarm_times_data(dialog_manager, **kwargs):
    alarm_times = await get_alarm_times()
    return {'alarm_times': alarm_times}
