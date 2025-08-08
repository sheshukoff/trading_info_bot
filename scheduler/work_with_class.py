import time
from connection_okx.get_data import safe_to_csv_file
from strategies.strategies import rsi_strategy, ema_strategy
from .scheduler import Scheduler
import asyncio
import random

SCHEDULERS = {}


async def add_scheduler(scheduler_dict, function, ticker, timeframe):
    key = f"{ticker}_{timeframe}"
    if key in scheduler_dict.keys():
        print(f"⛔ Задача {key} уже существует, не добавляем.")
        return scheduler_dict.get(key)

    s = await Scheduler.create(function, timeframe, ticker=ticker, timeframe=timeframe)
    scheduler_dict[key] = s
    print(f"✅ Добавлена задача: {key}")
    return s


async def main_2(ticker, timeframe):
    df = await safe_to_csv_file(ticker, timeframe)
    print('работет rsi_strategy')
    print(await rsi_strategy(df))
    print('работет ema_strategy')
    print(await ema_strategy(df))


async def main():
    # Список монет (можешь дополнить своими)
    coins = ["BTC-USDT"]  # "SOL-USDT", "XRP-USDT"

    # Список таймфреймов (например, как на биржах или в TradingView)
    timeframes = ["1m"]  # "4H", "1D"

    pairs = [(coin, tf) for coin in coins for tf in timeframes]
    print(pairs)

    count = 0

    while count < 1:
        random_element = random.choice(pairs)
        ticker, timeframe = random_element
        await add_scheduler(SCHEDULERS, main_2, ticker, timeframe)
        await asyncio.sleep(1)
        count += 1
        print(len(SCHEDULERS))
        print(SCHEDULERS.keys())

    print(len(SCHEDULERS.keys()))
    run_tasks = []
    for scheduler in SCHEDULERS.values():
        run_tasks.append(scheduler.run_async())
        print('run_tasks', run_tasks)
    await asyncio.gather(*run_tasks)


if __name__ == '__main__':
    asyncio.run(main())
