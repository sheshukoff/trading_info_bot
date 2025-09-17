from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from connection_oracle.queries_to_oracle import get_coins, get_alarm_times


main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Выбранные стратегии'), KeyboardButton(text='Добавить стратегию')],
    [KeyboardButton(text='Удалить стратегию'), KeyboardButton(text='Информация о боте')]
],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню'
)


async def to_disclaimer():
    next_disclaimer = InlineKeyboardBuilder()
    next_disclaimer.add(InlineKeyboardButton(text='Далее ...', callback_data='next'))
    return next_disclaimer.adjust(1).as_markup()


async def add_strategy():
    strategy_keyboard = InlineKeyboardBuilder()
    strategy_keyboard.add(InlineKeyboardButton(text='Стратегия RSI 14', callback_data='rsi_strategy'))
    strategy_keyboard.add(InlineKeyboardButton(text='Стратегия EMA', callback_data='ema_strategy'))
    return strategy_keyboard.adjust(2).as_markup()


async def coins():
    coins_keyboard = InlineKeyboardBuilder()

    for coin in await get_coins():
        print(coin)
        coins_keyboard.add(InlineKeyboardButton(text=coin, callback_data='add coin'))
    return coins_keyboard.adjust(2).as_markup()


async def alarm_times():
    alarm_times_keyboard = InlineKeyboardBuilder()

    for alarm_time in await alarm_times():
        print(alarm_time)
        alarm_times_keyboard.add(InlineKeyboardButton(text=alarm_time, callback_data='add alarm time'))
    return alarm_times_keyboard.adjust(1).as_markup()
