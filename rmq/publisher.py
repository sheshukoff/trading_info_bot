import aiorabbit
from dotenv import dotenv_values

config = dotenv_values("../.env")
RABBITMQ_URL = config.get("RABBITMQ_URL")


async def periodic_publisher(message):
    try:
        async with aiorabbit.connect(RABBITMQ_URL) as client:
            await client.confirm_select()
            await client.queue_declare('periodic_queue')

            success = await client.publish(
                routing_key='periodic_queue',
                message_body=message,
                content_type='text/plain',
                exchange='',  # необязательно
                app_id='periodic_publisher'  # необязательно
            )

            if success:
                print(f'Отправлено: {message}')
            else:
                print('Ошибка отправки сообщения!!!')

    except Exception as e:
        print(f'Error: {e}')
