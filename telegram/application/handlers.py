from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from rmq.rabbit import send_to_queue
from aiogram import types
import keyboards as kb

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message):
    await message.reply('Привет!', reply_markup=kb.main)


@router.message()
async def handler_reminder(message: types.Message):  # для обработки входящих сообщений
    user_message = message.text
    print('id пользователя', message.from_user.id)
    correlation_id = str(message.chat.id)

    reply_queue = f'response_{message.chat.id}'

    await message.answer(f'Отпарвляю {user_message} на обработку...')

    await send_to_queue(user_message,
                        reply_to=reply_queue,
                        correlation_id=correlation_id,
                        routing_key='any_message')


@router.message()
async def handle_number(message: types.Message):
    try:
        number = int(message.text)
        # Сохраняем чистый chat.id без префикса
        correlation_id = str(message.chat.id)
        # Формируем имя очереди для ответа
        reply_queue = f"response_{message.chat.id}"

        await message.answer(f"⌛ Отправляю {number} на обработку...")
        # Передаем correlation_id и reply_queue отдельно
        await send_to_queue(number,
                            reply_to=reply_queue,
                            correlation_id=correlation_id,
                            routing_key='tasks')

    except ValueError:
        await message.answer("❌ Пожалуйста, отправьте целое число!")


# @router.message(Command('help'))
# async def command_help_handler(message: Message):
#     await message.answer('Это команда /help')
#
#
# @router.message(F.text == 'Как дела?')
# async def how_are_you(message: Message):
#     await message.answer('ОК!')
#
#
# @router.message(F.photo)
# async def get_photo(message: Message):
#     await message.answer(f'ID фото {message.photo[-1].file_id}')
#
#
# @router.message(Command('get_photo'))
# async def get_photo(message: Message):
#     await message.answer_photo(
#         photo='https://petsitters.by/uploads/cache/750x500/02/48/86/image1711981679_EJI16nZVbKErYZpN.jpg',
#         caption='На держи мопса'
#     )
#
#
# @router.callback_query(F.data == 'catalog')
# async def catalog(callback: CallbackQuery):
#     await callback.answer('Вы выбрали каталог')
#     await callback.message.edit_text('Привет!', reply_markup=kb.settings)
#
#
# # def send_rsi_4h
