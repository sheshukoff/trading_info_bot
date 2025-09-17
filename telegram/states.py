from aiogram.fsm.state import State, StatesGroup


class MainSG(StatesGroup):
    start = State()
    disclaimer = State()
    guide = State()
    strategies = State()
    coins = State()
    alarm_times = State()
    summary = State()
