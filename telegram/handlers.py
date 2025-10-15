from aiogram_dialog import DialogManager, ChatEvent, StartMode

from aiogram_dialog.widgets.kbd import ManagedCheckbox, Select
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from telegram.app.keyboards import main_menu
from telegram.states import MainSG
from rmq.consumer import send_to_queue
from telegram.api import add_user

reports = {}

router = Router()


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.start, mode=StartMode.RESET_STACK)


async def on_start_menu(callback, button, manager: DialogManager):
    await manager.done()  # закрываем диалог

    # безопасно получаем chat_id
    if manager.event.message:
        chat_id = manager.event.message.chat.id
        user_name = manager.event.message.chat.username
    else:
        chat_id = manager.event.from_user.id
        user_name = manager.event.from_user.username

    await add_user(chat_id, user_name)
    await manager.event.bot.send_message(
        chat_id=chat_id,
        text="📋 Главное меню:",
        reply_markup=main_menu
    )


def make_on_selected(key: str, next_state):
    """Фабрика универсальных обработчиков выбора"""
    async def handler(c: CallbackQuery, s: Select, manager: DialogManager, selected: str):
        manager.dialog_data[key] = selected
        await manager.switch_to(next_state)
    return handler


async def on_add_strategy(c, b, manager: DialogManager):
    await manager.switch_to(MainSG.strategies)


async def on_agree_changed(event: ChatEvent, checkbox: ManagedCheckbox, manager: DialogManager):
    manager.dialog_data["agree"] = checkbox.is_checked()
    print("Agree status:", manager.dialog_data["agree"])


def selected_data(key: str, alias: str):
    """
    Универсальная фабрика getter'ов для dialog_data.
    key   - ключ в dialog_data
    alias - как будет называться в шаблоне
    """
    async def getter(dialog_manager: DialogManager, **kwargs):
        return {alias or key: dialog_manager.dialog_data.get(key, [])}
    return getter


async def selected_data_value(dialog_manager, key):
    return dialog_manager.dialog_data.get(key, [])


async def on_choose_strategy(c, b, manager: DialogManager):
    # собираем выбранные данные
    strategy = await selected_data_value(manager, "strategies")
    coins = await selected_data_value(manager, "coins")
    timeframe = await selected_data_value(manager, "alarm_times")

    if manager.event.message:
        chat_id = manager.event.message.chat.id
    else:
        chat_id = manager.event.from_user.id

    if f'{strategy}_{coins}_{timeframe}' not in reports:
        reports[f'{strategy}_{coins}_{timeframe}'] = [chat_id]
    else:
        reports[f'{strategy}_{coins}_{timeframe}'].append(chat_id)

    await send_to_queue(strategy, coins, timeframe, chat_id, 'test')  # кладем в RabbitMQ

    await manager.switch_to(MainSG.summary)


@router.message(F.text == 'Информация о боте')
async def info_about_bot(message: Message):
    await message.reply('Дополнительная информация о боте')


@router.message(F.text == 'Добавить стратегию')
async def choose_strategy(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.strategies, mode=StartMode.RESET_STACK)

