import asyncio
import aiorabbit
import json
from telegram.api import add_job
from dotenv import dotenv_values

config = dotenv_values("../.env")
RABBITMQ_URL = config.get("RABBITMQ_URL")

strategies = {
    "RSI 14": ("RSI 14", 'process_market_data'),
    "EMA/WMA": ("EMA/WMA", 'process_market_data'),
}


async def send_to_queue(strategy: str, coin: str, timeframe: str, chat_id: int, name_queue: str):
    async with aiorabbit.connect(RABBITMQ_URL) as client:
        print('Подключено')
        await client.confirm_select()
        await client.queue_declare(name_queue)

        message = {
            'strategy': strategy,
            'coin': coin,
            'timeframe': timeframe,
            'chat_id': chat_id
        }

        success = await client.publish(
            exchange="",
            routing_key=name_queue,
            message_body=json.dumps(message).encode("utf-8")
        )
        if success:
            print(f"[>] Сообщение отправлено в очередь -> {message}")
        else:
            print(f"[!] Не удалось отправить сообщение -> {message}")


async def consume_message():
    try:
        async with aiorabbit.connect(RABBITMQ_URL) as client:
            print('Подключено')
            await client.queue_declare('test')  # Создание очереди
            async for message in client.consume('test'):  # достаю из очереди по одному сообщению
                print(f'[x] Получено: {message.body.decode()}')  # Вывод собщений кто то написал

                result = json.loads(message.body.decode("utf-8"))

                strategy = result.get('strategy')
                coin = result.get('coin')
                timeframe = result.get('timeframe')

                strategy_name, load_function = strategies[strategy]
                print(strategy_name, load_function)

                await add_job(load_function, coin, timeframe)

                if message.delivery_tag:
                    await client.basic_ack(message.delivery_tag)  # Сообщения которые прочел пользователь
    except Exception as e:
        print(f'Error: {e}')


if __name__ == '__main__':
    try:
        asyncio.run(consume_message())
    except KeyboardInterrupt:
        print('exit')

