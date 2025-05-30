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


def group_tickers(tickers: list) -> dict:
    df_tickers = pd.DataFrame(tickers, columns=['tickers'])
    df_tickers['stablecoin'] = df_tickers['tickers'].apply(lambda x: x.split('-')[1])
    grouped = df_tickers.groupby("stablecoin")["tickers"].apply(list).to_dict()
    return grouped


def write_to_json_file(data: dict) -> json:
    with open("grouped_tickers.json", "w") as f:
        json.dump(data, f, indent=2)


tickers = get_tickers()

grouped_tickers = group_tickers(tickers)

write_to_json_file(grouped_tickers)

