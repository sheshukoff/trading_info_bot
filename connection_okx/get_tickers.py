import requests
import pandas as pd
import json


def get_tickers(inst_type='SPOT') -> list:
    endpoint = '/api/v5/market/tickers'
    params = {
        'instType': inst_type
    }

    url = 'https://www.okx.com' + endpoint
    response = requests.get(url, params=params)

    all_tickers = []

    for ticker in response.json()['data']:
        all_tickers.append(ticker['instId'])

    return all_tickers
