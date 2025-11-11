import asyncio
from connection_okx.get_data import get_data_okx
from strategies.strategies import rsi_strategy, ema_strategy
from scheduler.scheduler import Scheduler

SCHEDULERS = {}

strategies = {
    1: ("RSI стратегия", get_data_okx, rsi_strategy),
    2: ("EMA стратегия", get_data_okx, ema_strategy),
}


async def add_task(load_function, strategy_function, ticker, timeframe, strategy_name):
    scheduler_key = f"{ticker} {timeframe}"

    if scheduler_key not in SCHEDULERS:
        scheduler = await Scheduler.create(load_function, strategy_function, timeframe, ticker=ticker, timeframe=timeframe)
        task = asyncio.create_task(scheduler.run_async())
        SCHEDULERS[scheduler_key] = {
            "scheduler": scheduler,
            "task": task,
            "ticker": ticker,
            "timeframe": timeframe,
            "strategy_name": strategy_name
        }
        print(f"✅ Создан новый Scheduler для {scheduler_key}")
    else:
        print(f"ℹ️ Используем существующий Scheduler для {scheduler_key}")


async def remove_task(ticker, timeframe):
    scheduler_key = f"{ticker} {timeframe}"

    if scheduler_key not in SCHEDULERS:
        print(f"⚠️ Планировщик {scheduler_key} не найден")
        return

    scheduler_data = SCHEDULERS[scheduler_key]

    task = scheduler_data.get('task')
    task.cancel()

    del SCHEDULERS[scheduler_key]

    print(f"🛑 Планировщик {scheduler_key} удалён")


async def choose_strategy():
    while True:
        for number, name in strategies.items():
            print(number, name)

        strategy_num = int(await asyncio.to_thread(input, "Выберите стратегию (номер): "))

        strategy_name, load_function, strategy_function = strategies[strategy_num]

        coin = await asyncio.to_thread(input, 'Введите монету (например: BTC-USDT): ')
        timeframe = await asyncio.to_thread(input, 'Введите таймфрейм (например: 1h): ')

        # print(coin.strip().upper(), timeframe.strip())
        await asyncio.sleep(0.1)
        yield coin.strip().upper(), timeframe.strip(), load_function, strategy_function, strategy_name


async def runner_for_generator3():
    async for ticker, timeframe, load_function, strategy_func, strategy_name in choose_strategy():
        print(ticker, timeframe, load_function, strategy_func, strategy_name)
        await asyncio.sleep(0.1)
        await add_task(load_function, strategy_func, ticker, timeframe=timeframe, strategy_name=strategy_name)


async def main():
    tasks = [
        asyncio.create_task(runner_for_generator3())
    ]

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')