import requests
import asyncio

URL = 'http://127.0.0.1:8000'
HEADERS = {'Content-Type': 'application/json'}


async def add_user(telegram_id: int, telegram_name: str):
    body = {
        "telegram_id": telegram_id,
        "telegram_name": telegram_name
    }

    end_point = f'{URL}/users'
    response = requests.post(end_point, json=body, headers=HEADERS)
    await asyncio.sleep(0.1)
    print(response.json())
    return response.json()['id']


async def delete_user(telegram_id: int):
    body = {
        "telegram_id": telegram_id
    }

    end_point = f'{URL}/users'
    response = requests.delete(end_point, json=body, headers=HEADERS)
    await asyncio.sleep(0.1)
    return response.json()['id']


async def user_strategies(telegram_id: int):
    params = {
        "telegram_id": telegram_id
    }

    end_point = f'{URL}/strategies'
    response = requests.get(end_point, params=params, headers=HEADERS)
    print(response.json())
    await asyncio.sleep(0.1)
    return response.json()['strategies']
