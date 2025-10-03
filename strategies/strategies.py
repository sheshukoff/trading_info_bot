import asyncio
import textwrap

import pandas as pd
from indicators.indicators import ema_5, ema_12, ema_25, wma_50, rsi_14
from rmq.publisher import periodic_publisher


def format_price(price: float, small_digit: int = 6) -> str:
    """
    Форматирует цену монеты:
    - Без экспоненты
    - Показывает заданное количество значащих цифр (по умолчанию 6)
    - Убирает лишние нули и точку в конце
    """
    if price == 0:
        return "0"

    # формируем строку с нужным количеством значащих цифр
    formatted = f"{price:.{small_digit}g}"

    # если вдруг Python вернул экспоненту — переведём в float с фиксированным количеством знаков
    if "e" in formatted or "E" in formatted:
        formatted = f"{price:.{small_digit + 2}f}"

    # убираем хвостовые нули и лишнюю точку
    return formatted.rstrip("0").rstrip(".")


async def get_last_close(df: pd.DataFrame) -> float:
    return df['close'].iloc[-1]


async def get_last_time(df: pd.DataFrame):
    return df['ts'].iloc[-1]


async def get_last_rsi(df: pd.DataFrame):
    return rsi_14(df).iloc[-1]


async def rsi_strategy(df: pd.DataFrame, ticker: str, timeframe: str) -> None:
    last_price = await get_last_close(df)
    rsi_14_last = await get_last_rsi(df)
    print(rsi_14_last)
    last_time = await get_last_time(df)

    message, signal_active = await coin_information_rsi(last_price, rsi_14_last, last_time, ticker, timeframe)

    if signal_active:
        data = {
            'message': message,
            'report': f'RSI 14_{ticker}_{timeframe}',
        }

        await periodic_publisher(data)


async def ema_strategy(df: pd.DataFrame, ticker: str, timeframe: str) -> None:
    ema_5_last = ema_5(df).iloc[-1]
    ema_12_last = ema_12(df).iloc[-1]
    ema_25_last = ema_25(df).iloc[-1]
    wma_50_last = wma_50(df).iloc[-1]
    # print(ema_5_last, ema_12_last, ema_25_last, wma_50_last)
    close_last = df['close'].iloc[-1]
    last_time = await get_last_time(df)

    long_signal = ema_5_last > ema_12_last and ema_12_last > ema_25_last and close_last > wma_50_last
    short_signal = ema_5_last < ema_12_last and ema_12_last < ema_25_last and close_last < wma_50_last
    message = await summarize_trend_signal(close_last, long_signal, short_signal, last_time, ticker, timeframe)

    data = {
        'message': message,
        'report': f'EMA/WMA_{ticker}_{timeframe}',
    }

    await periodic_publisher(data)


async def coin_information_rsi(last_price: float, last_rsi_value: float, last_time: str, ticker: str,
                               timeframe: str) -> tuple:
    if last_rsi_value < 30:
        message = textwrap.dedent(f"""
        📊 <b>Стратегия на отскок цены RSI 14</b>
        📈 Информация по монете: <b>{ticker}</b> | Таймфрейм: <b>{timeframe}</b>
        ────────────────────────────
        💰 Цена закрытия: <b>{format_price(last_price)}</b> USDT
        📊 RSI (14): <b>{last_rsi_value:.2f}</b>
        🕒 Время: {last_time}
        ────────────────────────────
        Цели:
        1️⃣ Первый TP: <b>{last_price * 1.03:.2f}</b> (3% движения)
        2️⃣ Второй TP: <b>{last_price * 1.05:.2f}</b> (5% движения)
        3️⃣ Третий TP: <b>{last_price * 1.08:.2f}</b> (8% движения)
        """)

        return message, True
    return None, False


async def summarize_trend_signal(close: float, long_signal: bool, short_signal: bool, last_time: str, ticker: str,
                                 timeframe: str) -> str:
    if long_signal == short_signal:
        signal_text = '⏸️ WAIT'
    elif long_signal:
        signal_text = '🔼 LONG'
    elif short_signal:
        signal_text = '🔽 SHORT'
    else:
        signal_text = '❓ Неизвестный сигнал'

    message = textwrap.dedent(f"""
    📊 <b>Трендовая стратегия EMA/WMA</b>
    📈 Информация по монете: <b>{ticker}</b> 
    🕒 Таймфрейм: <b>{timeframe}</b>
    ────────────────────────────
    💰 Цена закрытия: <b>{format_price(close)}</b> USDT
    📍 Сигнал стратегии: <b>{signal_text}</b>
    🕒 Время: {last_time}
    """)

    return message


async def main():
    df = pd.read_csv('../BTC-USDT_1m.csv')
    print(df.dtypes)
    print(await rsi_strategy(df, "BTC-USDT", '1m'))
    # print(await ema_strategy(df, ticker))


if __name__ == '__main__':
    asyncio.run(main())

# Посмотреть примеры как работает сначала один отработал и пошел делать другое
# Сначала получил информацию с биржи OKX, затем вывел информацию о решении покупки продажи и ожидания
# https://github.com/stelmakhdigital/Predict_Stock_and_Crypto_for_Invest аналог проекта
