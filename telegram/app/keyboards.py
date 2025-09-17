from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Выбранные стратегии'), KeyboardButton(text='Добавить стратегию')],
    [KeyboardButton(text='Удалить стратегию'), KeyboardButton(text='Информация о боте')]
],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню'
)
