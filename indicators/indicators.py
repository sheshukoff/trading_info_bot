import talib as ta
import pandas as pd


def rsi_14(df: pd.DataFrame) -> pd.Series:
    s = pd.Series(ta.RSI(df['close'], timeperiod=14), name='rsi_14')
    return s.round(2)


def ema_x(df: pd.DataFrame, time_period, name):
    s = pd.Series(ta.EMA(df['close'], timeperiod=time_period), name=name)
    s = s.round(1)
    return s


def ema_5(df: pd.DataFrame) -> pd.Series:
    return ema_x(df, 5, 'EMA_5')


def ema_12(df: pd.DataFrame) -> pd.Series:
    return ema_x(df, 12, 'EMA_12')


def ema_25(df: pd.DataFrame) -> pd.Series:
    return ema_x(df, 25, 'EMA_25')


def wma_50(df: pd.DataFrame) -> pd.Series:
    part_processing = (df['high'] + df['lowest']) / 2
    s = pd.Series(ta.WMA(part_processing, timeperiod=50), name='WMA_50')
    return s.round(1)


if __name__ == '__main__':
    states = {}

    df = pd.read_csv('../BTC-USDT_1m.csv')
    ema_5 = ema_5(df).iloc[-1]
    ema_12 = ema_12(df).iloc[-1]
    ema_25 = ema_25(df).iloc[-1]
    wma_50 = wma_50(df).iloc[-1]
    close_last = df['close'].iloc[-1]

    rsi_14 = rsi_14(df).iloc[-1]
    print(rsi_14)

    if rsi_14 < 30:
        print('buy')

    long_signal = ema_5 > ema_12 and ema_12 > ema_25 and close_last > wma_50
    print(long_signal)
    short_signal = ema_5 < ema_12 and ema_12 < ema_25 and close_last < wma_50


