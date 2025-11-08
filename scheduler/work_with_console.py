import asyncio
from connection_okx.get_data import get_history_data_okx
from strategies.strategies import rsi_strategy, ema_strategy
from scheduler.scheduler import Scheduler

SCHEDULERS = {}
RUN_TASKS = {}

strategies = {
    1: ("RSI стратегия", get_data_okx, rsi_strategy),
    2: ("EMA стратегия", get_data_okx, ema_strategy),
}


async def add_task(load_function, strategy_function, ticker, timeframe, strategy_name):
    scheduler_key = f"{ticker}_{timeframe}"

    # если уже есть scheduler для этой пары → не создаём новый
    if scheduler_key not in SCHEDULERS:
        scheduler = await Scheduler.create(load_function, strategy_function, timeframe, ticker=ticker, timeframe=timeframe)
        task = asyncio.create_task(scheduler.run_async())
        SCHEDULERS[scheduler_key] = {
            "scheduler": scheduler,
            "task": task,
            "ticker": ticker,
            "timeframe": timeframe,
        }
        RUN_TASKS[scheduler_key] = []
        print(f"✅ Создан новый Scheduler для {scheduler_key}")
    else:
        print(f"ℹ️ Используем существующий Scheduler для {scheduler_key}")
        scheduler = SCHEDULERS[scheduler_key]['scheduler']
        await scheduler.add_strategy(strategy_function)

    if any(s['strategy_name'] == strategy_name for s in RUN_TASKS.get(scheduler_key, [])):
        print(f"⛔ Стратегия {strategy_name} уже подключена к {scheduler_key}")
        return

    # добавляем стратегию
    RUN_TASKS[scheduler_key].append({
        "strategy_name": strategy_name,
        "strategy_func": strategy_function,
    })

    print(f"✅ Добавлена стратегия {strategy_name} к {scheduler_key}")


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