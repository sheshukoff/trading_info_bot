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


async def add_job(load_function, ticker, timeframe):
    body = {
        "load_function": load_function,
        "ticker": ticker,
        "timeframe": timeframe
    }

    end_point = f'{URL}/add_job'

    response = requests.post(end_point, json=body, headers=HEADERS)
    print(response.json())
    await asyncio.sleep(0.1)
    return response.json()['ticker']


async def delete_job(job_id):
    body = {
        "job_id": job_id
    }

    end_point = f'{URL}/remove_job'
    response = requests.delete(end_point, json=body, headers=HEADERS)
    await asyncio.sleep(0.1)
    return response.json()['job_id']


async def add_user_strategy(telegram_id, strategy, ticker, timeframe):
    body = {
        "telegram_id": telegram_id,
        "strategy": strategy,
        "ticker": ticker,
        "timeframe": timeframe
    }

    end_point = f'{URL}/using_strategy'

    response = requests.post(end_point, json=body, headers=HEADERS)
    print(response.json())
    await asyncio.sleep(0.1)
    return response.json()['ticker'], response.json()['timeframe']


async def delete_user_strategy(telegram_id, strategy, ticker, timeframe):
    body = {
        "telegram_id": telegram_id,
        "strategy": strategy,
        "ticker": ticker,
        "timeframe": timeframe
    }

    end_point = f'{URL}/using_strategy'

    response = requests.delete(end_point, json=body, headers=HEADERS)
    await asyncio.sleep(0.1)
    return response.json()['strategy'], response.json()['ticker'], response.json()['timeframe']


async def delete_all_user_strategy(telegram_id):
    body = {
        "telegram_id": telegram_id,
    }

    end_point = '/using_strategy{user}'
    full_url = URL + end_point

    response = requests.delete(full_url, json=body, headers=HEADERS)
    await asyncio.sleep(0.1)
    return response.json()['telegram_id']


async def get_max_strategy_user(telegram_id: int):
    params = {
        "telegram_id": telegram_id
    }

    end_point = f'{URL}/users'
    response = requests.get(end_point, params=params, headers=HEADERS)
    print(response.json())
    await asyncio.sleep(0.1)
    return response.json()['max_strategies_user']
