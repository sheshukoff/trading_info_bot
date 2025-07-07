from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

import app.keyboards as kb

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message):
    await message.reply('Привет!', reply_markup=kb.main)


@router.message(Command('help'))
async def command_help_handler(message: Message):
    await message.answer('Это команда /help')


@router.message(F.text == 'Как дела?')
async def how_are_you(message: Message):
    await message.answer('ОК!')


@router.message(F.photo)
async def get_photo(message: Message):
    await message.answer(f'ID фото {message.photo[-1].file_id}')


@router.message(Command('get_photo'))
async def get_photo(message: Message):
    await message.answer_photo(
        photo='https://petsitters.by/uploads/cache/750x500/02/48/86/image1711981679_EJI16nZVbKErYZpN.jpg',
        caption='На держи мопса'
    )


@router.callback_query(F.data == 'catalog')
async def catalog(callback: CallbackQuery):
    await callback.answer('Вы выбрали каталог')
    await callback.message.edit_text('Привет!', reply_markup=kb.settings)


# def send_rsi_4h
