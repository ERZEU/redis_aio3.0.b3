from contextlib import suppress
from loguru import logger

from aiogram import Router
from aiogram import F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram import types
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.keyboard import InlineKeyboardBuilder

from backend.Keyboards import NumbersCallFactory

router = Router()


@router.callback_query(NumbersCallFactory.filter(F.action == "switch"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    keyboard_builder = InlineKeyboardBuilder()

    keyboard = callback.message.reply_markup.inline_keyboard
    key_pressed = callback.data

    for key in keyboard[:len(keyboard)-1]:
        for but in key:
            if but.callback_data == key_pressed:
                but.text = but.text.replace("🔵", "🔘")
            else:
                but.text = but.text.replace("🔘", "🔵")
            keyboard_builder.add(but)

    data_mas = key_pressed.split(":")

    keyboard_builder.button(text="Подтвердить",
                            callback_data=NumbersCallFactory(module=f'{data_mas[1]}_CONF',
                                                             value="confirm",
                                                             action=data_mas[2]))
    keyboard_builder.adjust(1)
    keyboard_builder.button(text="Отмена",
                            callback_data=NumbersCallFactory(module=data_mas[1],
                                                             value="cancel",
                                                             action="cancel"))

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(keyboard_builder.as_markup())


@router.callback_query(NumbersCallFactory.filter(F.action == "pressed"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer(text="Подтвержденный выбор изменить нельзя!")


@router.callback_query(NumbersCallFactory.filter(F.action == "cancel"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text="Действия отменены.")
    await state.clear()


@router.callback_query(NumbersCallFactory.filter(F.action == "err"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer(text="Сначала виберите действие!")


@router.message()
@logger.catch
async def stage(message: Message, state: FSMContext):
    logger.debug(f'User : {message.from_user.id}  send: {message.text}')
    await message.answer(text='Я такого не умею!')