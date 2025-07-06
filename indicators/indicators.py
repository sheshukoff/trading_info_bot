import pandas as pd
import talib as ta


# ema5    = ta.ema(close, 5)
# ema12   = ta.ema(close, 12)
# ema25   = ta.ema(close, 25)
# wma55hl2 = ta.wma(hl2, 50)

def rsi_indicator(df: pd.DataFrame) -> pd.DataFrame:
    df['RSI_14'] = ta.RSI(df['close'], timeperiod=14)
    df['RSI_14'] = round(df['RSI_14'], 2)
    return df


def ema_5_indicator(df: pd.DataFrame) -> pd.DataFrame:
    df['EMA_5'] = ta.EMA(df['close'], timeperiod=5)
    df['EMA_5'] = df['EMA_5'].round(1)
    return df


def ema_12_indicator(df: pd.DataFrame) -> pd.DataFrame:
    df['EMA_12'] = ta.EMA(df['close'], timeperiod=12)
    df['EMA_12'] = df['EMA_12'].round(1)
    return df


df = pd.read_csv('../connection_okx/BTC-USDT.csv')

df = df.sort_values(by='ts')
print(df.head())

rsi_indicator(df)
print(ema_5_indicator(df).tail(10))
