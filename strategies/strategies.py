import asyncio

import pandas as pd
from indicators.indicators import ema_5, ema_12, ema_25, wma_50, rsi_14


async def get_last_close(df: pd.DataFrame) -> float:
    return df['close'].iloc[-1]


async def get_last_time(df: pd.DataFrame):
    return df['ts'].iloc[-1]


async def get_last_rsi(df: pd.DataFrame):
    return rsi_14(df).iloc[-1]


async def rsi_strategy(df: pd.DataFrame, ticker: str) -> str | None:
    last_price = await get_last_close(df)
    rsi_14_last = await get_last_rsi(df)
    print(rsi_14_last)
    last_time = await get_last_time(df)

    return await coin_information_rsi(last_price, rsi_14_last, last_time, ticker)


async def ema_strategy(df: pd.DataFrame, ticker) -> str:
    ema_5_last = ema_5(df).iloc[-1]
    ema_12_last = ema_12(df).iloc[-1]
    ema_25_last = ema_25(df).iloc[-1]
    wma_50_last = wma_50(df).iloc[-1]
    # print(ema_5_last, ema_12_last, ema_25_last, wma_50_last)
    close_last = df['close'].iloc[-1]
    last_time = await get_last_time(df)

    long_signal = ema_5_last > ema_12_last and ema_12_last > ema_25_last and close_last > wma_50_last
    short_signal = ema_5_last < ema_12_last and ema_12_last < ema_25_last and close_last < wma_50_last
    # print(close_last, long_signal, short_signal, last_time)

    return await summarize_trend_signal(close_last, long_signal, short_signal, last_time, ticker)


async def coin_information_rsi(last_price: float, last_rsi_value: float, last_time: str, ticker: str) -> str:

    if last_rsi_value < 30:
        print(f"""
    📊 Стратегия на отскок цены RSI 14
    📈 Информация по монете: {ticker}
    ─────────────────────────────────────────
    💰 Цена закрытия:   {last_price:,.2f} USDT
    📊 RSI (14):        {last_rsi_value:.2f}
    🕒 Время:           {last_time}
    ─────────────────────────────────────────
    Цели
    Первый TP {last_price * 1.03:.2f} 3% движения
    Второй TP {last_price * 1.05:.2f} 5% движения
    Третий TP {last_price * 1.08:.2f} 8% движения
    """)
        return f"""
    📊 Стратегия на отскок цены RSI 14
    📈 Информация по монете: {ticker}
    ─────────────────────────────────────────
    💰 Цена закрытия:   {last_price:,.2f} USDT
    📊 RSI (14):        {last_rsi_value:.2f}
    🕒 Время:           {last_time}
    ─────────────────────────────────────────
    Цели
    Первый TP {last_price * 1.03:.2f} 3% движения
    Второй TP {last_price * 1.05:.2f} 5% движения
    Третий TP {last_price * 1.08:.2f} 8% движения
    """


async def summarize_trend_signal(close: float, long_signal: bool, short_signal: bool, last_time: str, ticker: str) -> str:
    if long_signal == short_signal:
        signal_text = '⏸️ Нет сигнала — наблюдаем'
    elif long_signal:
        signal_text = '🔼 LONG — рекомендуется покупать'
    elif short_signal:
        signal_text = '🔽 SHORT — рекомендуется продавать'
    else:
        signal_text = '❓ Неизвестный сигнал'
    print(f"""
    📊 Трендовая стратегия (EMA/WMA)
    📈 Информация по монете: {ticker}
    ────────────────────────────────────────────
    💰 Цена закрытия:     {close} USDT
    📍 Сигнал стратегии:  {signal_text}
    🕒 Время:             {last_time}
    """)

    return f"""
    📊 Трендовая стратегия (EMA/WMA)
    📈 Информация по монете: {ticker}
    ────────────────────────────────────────────
    💰 Цена закрытия:     {close} USDT
    📍 Сигнал стратегии:  {signal_text}
    🕒 Время:             {last_time}
    """


async def main():
    df = pd.read_csv('../BTC-USDT_1m.csv')
    print(df.dtypes)
    print(await rsi_strategy(df, "BTC-USDT"))
    # print(await ema_strategy(df, ticker))


if __name__ == '__main__':
    asyncio.run(main())


# Посмотреть примеры как работает сначала один отработал и пошел делать другое
# Сначала получил информацию с биржи OKX, затем вывел информацию о решении покупки продажи и ожидания
# https://github.com/stelmakhdigital/Predict_Stock_and_Crypto_for_Invest аналог проекта
