from aiogram.fsm.state import State, StatesGroup


class MainSG(StatesGroup):
    start = State()
    disclaimer = State()
    strategies = State()
    coins = State()
    alarm_times = State()
    ack_strategy = State()
    repeat_strategy = State()
    summary = State()
    remove_strategies = State()
    ack_remove_strategies = State()
