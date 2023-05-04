from contextlib import suppress

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from aiogram.dispatcher.filters.command import Command
from aiogram import F
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram import types

from backend.Keyboards import make_inline_keyboard, NumbersCallFactory, make_inline_keyboard_double, \
    make_inline_keyboard_one, replace_keyboard
from loguru import logger


router = Router()


class StateClsOptionalEquipment(StatesGroup):
    processing_state = State()  # состояние информирования
    processing_data = State()  # состояние предоставления документов
    prepare_data = State()  # состояние обработки документов
    confirmation = State()  # подтверждение запроса
    end_of_script = State()  # завершение сценария


type_ts = {"Новый" : "ts_new",
           "С пробегом(Б/У)" : "ts_by"}

module = "Optional_equipment"


@router.message(Command(commands=["addOE"]))
@logger.catch
async def cmd_start(message: Message, state: FSMContext):
    logger.info(f'User : {message.from_user.id}  send: {message.text}')
    await message.answer(text="Укажите состояние ТС на момент заключения договора",
                         reply_markup=make_inline_keyboard(par=type_ts,
                                                           module=module))
    await state.set_state(StateClsOptionalEquipment.processing_state)


@router.callback_query(NumbersCallFactory.filter(F.action == "ts_by"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    btn_pressed = callback.data.split(":")[3]
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=type_ts,
                                                                               key_pressed=btn_pressed,
                                                                               action="pressed"))
    await state.update_data(state_ts=btn_pressed)
    await callback.message.answer(text="Укажите вид оборудования")
    await state.set_state(StateClsOptionalEquipment.confirmation)


@router.callback_query(NumbersCallFactory.filter(F.action == "ts_new"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    btn_pressed = callback.data.split(":")[3]
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=type_ts,
                                                                               key_pressed=btn_pressed,
                                                                               action="pressed"))
    await state.update_data(state_ts=btn_pressed)
    await callback.message.answer(text=f'Для согласования установки дополнительного оборудования Вам необходимо:'
                              f'\n⦿ Запросить письмо у поставщика, подтверждающее сохранение гарантийных '
                              f'и/или иных обязательств, после установки вышеупомянутого оборудования'
                              f'\n⦿ Загрузить письмо от поставщика, подтверждающее сохранение гарантийных'
                              f'и/или иных обязательств, после установки вышеупомянутого оборудования.')
    await callback.message.answer(text=f'Готовы загрузить письмо от поставщика в настоящее время?',
                                  reply_markup=make_inline_keyboard_double(par={"Да": "yes", "Нет": "no"},
                                                                           module=module,
                                                                           action="yn"))
    await state.set_state(StateClsOptionalEquipment.processing_data)


@router.callback_query(NumbersCallFactory.filter(F.value == f'{module}_yes'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')
    await callback.message.answer(text="Приложите письмо от поставщика в виде файла")
    await state.set_state(StateClsOptionalEquipment.prepare_data)


@router.callback_query(NumbersCallFactory.filter(F.value == f'{module}_no'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')
    await callback.message.answer(text="После получения письма от поставщика снова выберите данный тип обращения в Telegram-боте")
    await state.clear()


@router.message(StateClsOptionalEquipment.prepare_data)
@logger.catch
async def stage(message: Message, state: FSMContext):
    """Обработка документов пользователя"""

    if document := message.document:
        logger.info(f'User : {message.from_user.id}  document_id: {document.file_id}')
        await state.update_data(document=document.file_id)

        # file = await bot.get_file(document.file_id)
        # file_path = file.file_path
        # await bot.download_file(file_path=file_path, destination=f"download_doc/{document.file_name}")

        await message.answer(text="Укажите вид оборудования")
        await state.set_state(StateClsOptionalEquipment.confirmation)
    else:
        await message.answer(text="Неверный формат сообщения")


@router.message(StateClsOptionalEquipment.confirmation)
@logger.catch
async def stage(message: Message, state: FSMContext):
    """Подтверждение заявки"""

    await state.update_data(type_equipment=message.text)

    logger.info(f'User : {message.from_user.id}  send: {message.text}')

    await message.answer(text="Подтвердите создание обращения по установке дополнительного оборудования",
                         reply_markup=make_inline_keyboard_double(par={"Подтвердить": "cfn", "Отмена": "cnl"},
                                                                  module=module,
                                                                  action="complete"))
    await state.set_state(StateClsOptionalEquipment.end_of_script)


@router.callback_query(NumbersCallFactory.filter(F.value == f'{module}_cfn'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Формирование заявки"""
    await callback.message.delete_reply_markup()

    await callback.message.answer(text="Благодарим за обращение! Заявка на установку дополнительного оборудования принята.")
    await state.clear()


@router.callback_query(NumbersCallFactory.filter(F.value == f'{module}_cnl'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    logger.info(f'User : {callback.message.from_user.id}  send: {callback.data}')
    await callback.message.answer(text="Действия отменены.")
    await state.clear()

