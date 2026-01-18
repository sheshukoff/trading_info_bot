from connection_oracle.get_queries import get_strategies, get_coins, get_alarm_times, get_quantity_strategy_user


async def get_strategies_data(dialog_manager, **kwargs):
    strategies = await get_strategies()
    return {"strategies": strategies}


async def get_coins_data(dialog_manager, **kwargs):
    coins = await get_coins()
    return {"coins": coins}


async def get_alarm_times_data(dialog_manager, **kwargs):
    alarm_times = await get_alarm_times()
    return {'alarm_times': alarm_times}


async def get_max_strategy_user(dialog_manager, **kwargs):
    if dialog_manager.event.message:
        chat_id = dialog_manager.event.message.chat.id
    else:
        chat_id = dialog_manager.event.from_user.id

    max_strategy = await get_quantity_strategy_user(chat_id)
    return {'limit': max_strategy}