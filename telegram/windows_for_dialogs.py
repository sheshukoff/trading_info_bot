from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group, Next, Row, Checkbox, Select, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format

from telegram.states import MainSG
from telegram.messages_for_dialog import start_comand_text, disclaimer_text
from telegram.data_for_dialog import get_strategies_data, get_coins_data, get_alarm_times_data
from telegram.handlers import (on_agree_changed, on_start_menu, on_add_strategy, make_on_selected, selected_data,
                               on_choose_strategy, return_start_menu)

selected_strategy = selected_data("strategies", "selected_strategy")
selected_coins = selected_data("coins", "selected_coins")
selected_alarm_times = selected_data("alarm_times", "selected_alarm_times")


window_start = Window(
        Const(start_comand_text),
        Next(Const('Далее')),
        state=MainSG.start
)

window_disclaimer = Window(
        Const(
            disclaimer_text
        ),
        Row(
            Checkbox(
                checked_text=Const("✅ Я согласен"),
                unchecked_text=Const("☑️ Я согласен"),
                id="agree",
                on_state_changed=on_agree_changed,
            ),
        ),
        Row(
            Button(
                Const("🚀 Начать"),
                id="start",
                on_click=lambda c, b, m: on_start_menu(c, b, m),
                when=lambda data, w, m: m.dialog_data.get("agree", False),  # доступно только если agree=True
            ),
        ),
        state=MainSG.disclaimer,
    )

window_strategy = Window(
        Const('Выберите стратегию'),
        Select(
            Format("{item}"),  # как отображаем элемент
            id="strategies",
            item_id_getter=lambda item: item,
            items="strategies",
            type_factory=str,
            on_click=make_on_selected("strategies", MainSG.coins),
        ),
        getter=get_strategies_data,
        state=MainSG.strategies,
    )

window_coins = Window(
        Const('Выберите монету'),
        ScrollingGroup(
            Select(
                Format('{item}'),
                id="coins",
                item_id_getter=lambda item: item,
                items='coins',
                type_factory=str,
                on_click=make_on_selected("coins", MainSG.alarm_times),
            ),
            id='coins_group',
            width=2,
            height=5,
        ),
        getter=get_coins_data,
        state=MainSG.coins,
    )

window_alarm_times = Window(
        Const('Выберите таймфрейм'),
        Group(
            Select(
                Format('{item}'),
                id='alarm_times',
                item_id_getter=lambda item: item,
                items='alarm_times',
                type_factory=str,
                on_click=make_on_selected("alarm_times", MainSG.ack_strategy),

            ),
            width=2,
        ),
        getter=get_alarm_times_data,
        state=MainSG.alarm_times,
    )

window_ack_strategy = Window(
    Format("Вы выбрали стратегию {selected_strategy} {selected_coins} {selected_alarm_times}"),
    Row(
        Button(Const('Подтвердить выбранную стратегию'), id='ack_strategy', on_click=on_choose_strategy)
    ),
    getter=[selected_strategy, selected_coins, selected_alarm_times],
    state=MainSG.ack_strategy
)

window_confirmation = Window(
        Format("Вы выбрали стратегию {selected_strategy} {selected_coins} {selected_alarm_times}"),
        Row(
            Button(Const('В меню'), id='to_menu', on_click=return_start_menu),
            Button(Const('Добавить еще'), id='add_strategy', on_click=on_add_strategy),
        ),
        getter=[selected_strategy, selected_coins, selected_alarm_times],
        state=MainSG.summary,
    )
