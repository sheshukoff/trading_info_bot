from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Каталог')],
    [KeyboardButton(text='RSI 14'), KeyboardButton(text='Цены по BTC')]
],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню'
)
