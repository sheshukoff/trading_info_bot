from aiogram_dialog import DialogManager, ChatEvent, StartMode

from aiogram_dialog.widgets.kbd import ManagedCheckbox, Select
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from telegram.app.keyboards import main_menu
from telegram.states import MainSG
from rmq.consumer import send_to_queue
import telegram.api as tg_api
from reports.reports import reports

router = Router()


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.start, mode=StartMode.RESET_STACK)


async def on_start_menu(callback, button, manager: DialogManager):
    await manager.done()  # закрываем диалог

    # безопасно получаем chat_id
    if manager.event.message:
        chat_id = manager.event.message.chat.id
        user_name = manager.event.message.chat.username or f"user_{chat_id}"
    else:
        chat_id = manager.event.from_user.id
        user_name = manager.event.from_user.username or f"user_{chat_id}"

    await tg_api.add_user(chat_id, user_name)
    await manager.event.bot.send_message(
        chat_id=chat_id,
        text="📋 Главное меню:",
        reply_markup=main_menu
    )


async def return_start_menu(callback, button, manager: DialogManager):
    if manager.event.message:
        chat_id = manager.event.message.chat.id
    else:
        chat_id = manager.event.from_user.id

    await manager.event.bot.send_message(
        chat_id=chat_id,
        text="📋 Главное меню:"
    )

    await manager.done()


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
    coin = await selected_data_value(manager, "coins")
    timeframe = await selected_data_value(manager, "alarm_times")

    if manager.event.message:
        chat_id = manager.event.message.chat.id
    else:
        chat_id = manager.event.from_user.id

    user_strategy = f'{strategy} {coin} {timeframe}'
    user_strategy_exists = await check_user_strategy(chat_id, user_strategy)

    if user_strategy_exists:
        await manager.switch_to(MainSG.repeat_strategy)
        return
    else:
        reports.add_user_strategy(chat_id, strategy, coin, timeframe)
        await send_to_queue(strategy, coin, timeframe, chat_id, 'test')  # кладем в RabbitMQ
        await manager.switch_to(MainSG.summary)


async def check_user_strategy(chat_id, strategy):
    user_strategies = reports.get_user_strategies(chat_id)

    if strategy in user_strategies:
        return True
    return False


async def get_user_strategies(dialog_manager: DialogManager, **kwargs):
    chat_id = dialog_manager.event.from_user.id

    user_strategies = reports.get_user_strategies(chat_id)

    if not user_strategies:
        user_strategies = ["Нет доступных стратегий"]

    return {"remove_strategies": user_strategies}


async def on_remove_strategies(c, b, manager: DialogManager):
    if manager.event.message:
        chat_id = manager.event.message.chat.id
    else:
        chat_id = manager.event.from_user.id

    # Получаем выбранные значения из мультиселекта напрямую
    widget = manager.find("remove_strategies")
    selected_strategies = widget.get_checked()

    print(f"Выбранные опции: {selected_strategies}")

    # Удаление стратегий пользователя из объекта reports
    for strategy in selected_strategies:
        reports.remove_user_strategy(chat_id, strategy)
        await reports.check_strategy(chat_id, strategy)

    # Сохраняем в dialog_data для передачи на следующий экран
    manager.dialog_data["selected"] = selected_strategies
    await manager.switch_to(MainSG.ack_remove_strategies)


async def get_removed_strategies(dialog_manager: DialogManager, **kwargs):
    selected_strategies = dialog_manager.dialog_data.get("selected", [])

    if not selected_strategies:
        return {"selected": "Вы не удалили не одной стратегии ❌"}

    text = ''

    for number, strategy in enumerate(selected_strategies, start=1):
        text += f"{number}. <b>{strategy}</b>\n"

    return {"selected": text}


@router.message(F.text == 'Информация о боте')
async def info_about_bot(message: Message):
    await message.reply('Дополнительная информация о боте')


@router.message(F.text == 'Добавить стратегию')
async def choose_strategy(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.strategies, mode=StartMode.RESET_STACK)


@router.message(F.text == 'Выбранные стратегии')
async def choosing_strategy(message: Message):
    chat_id = message.chat.id
    list_strategies = await tg_api.user_strategies(chat_id)

    text = "<b>📊 Ваши активные стратегии:</b>\n\n"

    if list_strategies:
        text += list_strategies
        # for number, strategy in enumerate(list_strategies, start=1):
        #     text += f"{number}.  <b>{strategy}</b>\n"

        await message.answer(text, parse_mode="HTML")
    else:
        await message.answer("У вас пока нет активных стратегий.")


@router.message(F.text == 'Удалить стратегию')
async def remove_strategy(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.remove_strategies, mode=StartMode.RESET_STACK)
