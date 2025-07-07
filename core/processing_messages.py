import aio_pika
import asyncio
from dotenv import dotenv_values

from aio_pika.exchange import Exchange
from aio_pika.queue import Queue
from aio_pika.message import IncomingMessage

config = dotenv_values("../.env")

RABBITMQ_URL = config.get("RABBITMQ_URL")

dictionary = {'купи батон': 'Напоминаю - купи батон',
              'хочу получать сигналы': 'Дисклаймер...',
              'Каталог': '''👋 Добро пожаловать!Этот Telegram-бот создан для помощи в анализе рынка криптовалют. Он предоставляет торговые сигналы на основе двух стратегий:

               📈 Стратегия 1: RSI 14
               Основана на классическом индикаторе относительной силы (RSI) с периодом 14. Помогает выявлять зоны перекупленности и перепроданности, чтобы находить возможные точки входа и выхода.

               📊 Стратегия 2: Трендовая
               Следует за трендом с использованием скользящих средних и других технических индикаторов, определяя направление движения рынка и фильтруя ложные сигналы.''',

              'RSI 14': 'Вы получаете сигналы по RSI 14',
              'Цены по BTC': 'Вы получаете цены по BTC'
}

# вся логика входящих и исходящих сообщений должна быть в worker.py


async def init_rabbit_mq():
    connection = await aio_pika.connect(RABBITMQ_URL)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    # Объявляем exchange для ответов
    exchange = await channel.declare_exchange(
        "responses",
        aio_pika.ExchangeType.DIRECT,
        durable=True
    )
    print('Типы init rabbit_mq', type(connection), type(channel), type(exchange))
    return connection, channel, exchange


async def processing_queue(queue: Queue, exchange: Exchange):
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                await received_message(message, exchange)


async def received_message(message: IncomingMessage, exchange: Exchange):
    print('message', type(message))
    try:
        user_message = message.body.decode()
        print(user_message, 'user_message')
        result = await processing_user_message(user_message)

        await publish_result(exchange, message, result)
        # await publish_result(exchange, user_message, result)

    except UnicodeDecodeError:
        print("Ошибка в декодировании")
    except KeyError:
        print("Ошибка в ключе словаря")
    except Exception as e:
        print(f"Ошибка в отправке сообщения: {e}")


async def processing_user_message(user_message: str):
    if user_message.isdigit():
        result = int(user_message) ** 2
    else:
        result = dictionary[user_message]

    if result == 'Дисклаймер...':
        result = 100500

    return result


async def publish_result(exchange: Exchange, message: IncomingMessage, result: str):
    print('message.from_user.id', message.user_id)
    await exchange.publish(  # для публикации ответов
        aio_pika.Message(
            body=str(result).encode(),
            correlation_id=message.correlation_id,  # Используем исходный correlation_id
            user_id=message.user_id
        ),
        routing_key="bot_responses_reminder",  # Очередь ответов она должна быть и в функции callback
    )


async def process_reminder():
    connection, channel, exchange = await init_rabbit_mq()
    print(connection, channel, exchange)

    queue = await channel.declare_queue("any_message", durable=True)  # эта строка должна создать новую очередь и брать из этой очереди
    print('очередь', type(queue))
    await processing_queue(queue, exchange)


async def process_tasks():
    connection = await aio_pika.connect(Config.RABBITMQ_URL)

    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)

    # Объявляем exchange для ответов
    exchange = await channel.declare_exchange(
        "responses",
        aio_pika.ExchangeType.DIRECT,
        durable=True
    )

    queue = await channel.declare_queue("tasks", durable=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    number = int(message.body.decode())
                    result = number ** 2
                    print(f"Обработано: {number} -> {result}")

                    # Отправляем результат в exchange
                    await exchange.publish(
                        aio_pika.Message(
                            body=str(result).encode(),
                            correlation_id=message.correlation_id,  # Используем исходный correlation_id
                        ),
                        routing_key="bot_responses",
                    )
                    print(f"Результат отправлен в exchange")
                except Exception as e:
                    print(f"Ошибка обработки: {e}")


async def main():
    await asyncio.gather(
        process_reminder()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')


# try:
#     await exchange.publish(
#         aio_pika.Message(
#             body=str(result).encode(),
#             correlation_id=message.correlation_id,  # Используем исходный correlation_id
#         ),
#         routing_key="bot_responses_reminder",  # Очередь ответов она должна быть и в функции callback
#     )
#     print(f"Результат отправлен в exchange")
# except Exception as e:
#     print(f'Ошибка в отправке сообщения {e}')


# async with queue.iterator() as queue_iter:
#     async for message in queue_iter:
#         async with message.process():
#             try:
#                 user_message = message.body.decode()
#                 if user_message.isdigit():
#                     result = int(user_message) ** 2
#                 else:
#                     result = dictionary[user_message]
#
#                 if result == 'Дисклаймер...':
#                     result = 100500
#
#                 while result == 'Дисклаймер...':
#                     time.sleep(5)
#                     await exchange.publish(  # для публикации ответов
#                         aio_pika.Message(
#                             body=str(result).encode(),
#                             correlation_id=message.correlation_id,  # Используем исходный correlation_id
#                         ),
#                         routing_key="bot_responses_reminder",  # Очередь ответов она должна быть и в функции callback
#                     )
#                 print(f"Результат отправлен в exchange")
#             except UnicodeDecodeError:
#                 print('Ошибка в декодирования')
#             except KeyError:
#                 print('Ошибка в ключе словаря')
#             except Exception as e:
#                 print(f'Ошибка в отправке сообщения {e}')



