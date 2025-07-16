# import telegram # почта
# import rabbit_mq # курьер по доставке сообщений
# import connection_okx # подключение к данным
# import strategies # данные
import asyncio
import processing_messages

import telegram.main as telegram
from scheduler.scheduler import Scheduler
from connection_okx.get_data import safe_to_csv_file

scheduler = Scheduler(safe_to_csv_file, '1m', ticker='BTC-USDT', timeframe='1m')

# scheduler(safe_to_csv_file, '1m', ticker='BTC-USDT', timeframe='1m')  # планировщик, который извлекает данные с
# с биржи OKX и сохраняет в csv file


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
