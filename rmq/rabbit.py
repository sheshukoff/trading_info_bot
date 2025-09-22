import aio_pika
from aiogram import Bot
from dotenv import dotenv_values

config = dotenv_values("../.env")

RABBITMQ_URL = config.get("RABBITMQ_URL")


async def send_to_queue(number: int, reply_to: str, correlation_id: str, routing_key: str):
    """Отправка числа в очередь на обработку"""
    connection = await aio_pika.connect(RABBITMQ_URL)
    channel = await connection.channel()

    await channel.default_exchange.publish(
        aio_pika.Message(
            body=str(number).encode(),
            reply_to=reply_to,
            correlation_id=correlation_id,  # Используем чистый chat.id
        ),
        routing_key=routing_key,
    )
    print(f'Обработка числа {number} отправлена в RabbitMQ...')
    await connection.close()


async def setup_consumer(bot: Bot):  # Принимаем bot вместо dp # Для ответов в телеграмм
    """Запуск потребителя для обработки ответов"""
    print('Запуск потребителя для обработки ответов')
    connection = await aio_pika.connect(RABBITMQ_URL)
    channel = await connection.channel()

    # Объявляем exchange для ответов
    exchange = await channel.declare_exchange(
        "responses",
        aio_pika.ExchangeType.DIRECT,
        durable=True
    )

    async def callback(message: aio_pika.IncomingMessage):
        print('Получен ответ из RabbitMQ')
        async with message.process():
            # Преобразуем correlation_id в int
            try:
                chat_id = int(message.correlation_id)
                result = message.body.decode()
                print(f'Отправка результата в Telegram чат {chat_id}')
                await bot.send_message(chat_id, result)  #✅
            except (ValueError, TypeError) as e:
                print(f"Ошибка преобразования chat_id: {e}")
            except Exception as e:
                print(f"Ошибка отправки сообщения: {e}")

    # Создаем временную очередь
    queue = await channel.declare_queue(exclusive=True)
    await queue.bind(exchange, routing_key="bot_responses_reminder")
    await queue.consume(callback)

    print('Потребитель запущен')
    return connection
