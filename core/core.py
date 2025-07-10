# import telegram # почта
# import rabbit_mq # курьер по доставке сообщений
# import connection_okx # подключение к данным
# import strategies # данные
import asyncio
import processing_messages

import telegram.main as telegram


async def main():
    await asyncio.gather(
        telegram.main(),
        processing_messages.main()
    )


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
