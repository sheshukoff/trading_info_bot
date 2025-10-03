import asyncio
import aiorabbit
import datetime
import json
from dotenv import dotenv_values

config = dotenv_values("../.env")
RABBITMQ_URL = config.get("RABBITMQ_URL")


async def periodic_publisher(message):
    try:
        async with aiorabbit.connect(RABBITMQ_URL) as client:
            await client.confirm_select()
            await client.queue_declare('periodic_queue')

            success = await client.publish(
                exchange="",
                routing_key='periodic_queue',
                message_body=json.dumps(message).encode("utf-8")
            )

            if success:
                print(f'Отправлено: {message}')
            else:
                print('Ошибка отправки сообщения!!!')

    except Exception as e:
        print(f'Error: {e}')


# core <- tasks
# core -> periodic_queue (5sec)

# message_count = 0
#
# while True:
#     message_count += 1
#
#     message_body = (
#         f'Сообщение #{message_count}'
#         f'отправлено в {datetime.datetime.now()}'
#     )

# await asyncio.sleep(5)