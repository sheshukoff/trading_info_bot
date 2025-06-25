# import time
#
#
# def test():
#     print('2 sec')
#
#
# def test2():
#     print('5 sec')
#
#
# while True:
#     test = test()
#     test2 = test2()
#     if test:
#         time.sleep(2)
#     elif test2:
#         time.sleep(5)

#  сделать не асинхронно вывод через 2 и 5 секунд -> постоянно


import random as rnd

import asyncio
import aioconsole

# class Person:
#     def __init__(self, name, age):
#         self.person_id = person_id
#         self.name = name
#         self.age = age
#
#
# person = Person('User1', 24)

dictionary_1 = {'RSI 14': 'Вы получаете сигналы по RSI 14',
                'Цены по BTC': 'Вы получаете цены по BTC'}


async def print_every_5_seconds():
    while True:
        print("Сообщение каждые 5 секунд")
        await asyncio.sleep(15)


async def print_every_3_seconds():
    while True:
        print("Сообщение каждые 3 секунды")
        await asyncio.sleep(10)


async def hello_input():
    while True:
        name = await aioconsole.ainput()
        print(f'Привет! {name} вы зарегистрировались!!!')
        await asyncio.sleep(5)


async def send_price_btc():
    btc_price = 105000

    while True:
        change_price = rnd.randint(-100, 100)
        btc_price += change_price
        yield btc_price
        await asyncio.sleep(2)


async def generate_price_btc():
    async for price in send_price_btc():
        print(f"Цена BTC: {price}")


async def main():
    await asyncio.gather(
        print_every_5_seconds(),
        print_every_3_seconds(),
        hello_input(),
        generate_price_btc()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')

## Взять за основу структуру в test.py и сделать примерно так же в worker.py
