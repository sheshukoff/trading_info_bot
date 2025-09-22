import asyncio
import aiorabbit

from scheduler.work_with_console import add_task
from connection_okx.get_data import get_data_okx
from strategies.strategies import rsi_strategy, ema_strategy

from dotenv import dotenv_values

config = dotenv_values("../.env")
RABBITMQ_URL = config.get("RABBITMQ_URL")


strategies = {
    "RSI 14": ("RSI 14", get_data_okx, rsi_strategy),
    "EMA/WMA": ("EMA/WMA", get_data_okx, ema_strategy),
}


async def consume_message():
    try:
        async with aiorabbit.connect(RABBITMQ_URL) as client:
            print('Подключено')
            await client.queue_declare('test')  # Создание очереди
            async for message in client.consume('test'):  # достаю из очереди по одному сообщению
                print(f'[x] Получено: {message.body.decode()}')  # Вывод собщений кто то написал
                result = message.body.decode()
                strategy, coin, timeframe = result.split(',')
                print(strategy.strip(), coin.strip(), timeframe.strip())

                strategy_name, load_function, strategy_function = strategies[strategy.strip()]
                print(strategy_name, load_function, strategy_function)

                await add_task(
                    load_function,
                    strategy_function,
                    coin.strip(),
                    timeframe=timeframe.strip(),
                    strategy_name=strategy_name
                )

                if message.delivery_tag:
                    await client.basic_ack(message.delivery_tag)  # Сообщения которые прочел пользователь
    except Exception as e:
        print(f'Error: {e}')


if __name__ == '__main__':
    try:
        asyncio.run(consume_message())
    except KeyboardInterrupt:
        print('exit')

#  Должно запустится код достающий данные из биржи

# 1 часть уже есть
# 2 часть
    # сообщение о том что делать отправить в Rabbit MQ
# 3 часть уже телеграмм должен слушать
# 4 при нажатии на кнопки отправлять
