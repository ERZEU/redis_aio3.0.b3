from contextlib import suppress
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, FSInputFile
from aiogram.dispatcher.filters.command import Command
from aiogram import F
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram import types

from backend.Keyboards import make_inline_keyboard, NumbersCallFactory, make_inline_keyboard_double, \
    make_inline_keyboard_one, replace_keyboard
from loguru import logger


router = Router()


class StateClsReorg(StatesGroup):
    processing_state = State()  # состояние информирования
    processing_data = State()  # состояние предоставления документов
    prepare_data = State()  # состояние обработки документов
    end_of_script = State()  # завершение сценария


methods_reorg = {
    "Слияние" : "merger",
    "Присоединение" : "accession",
    "Выделение" : "selection",
    "Разделение" : "separation",
    "Преобразование" : "transformation",
    "Другое" : "other",
}

methods_feedback = {
    "Данный Telegram бот" : "bot",
    "ЭДО" : "edo",
    "Электронная почта" : "email"
}

module = "Reorganization"


@router.message(Command(commands=["reorg"]))
@logger.catch
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(text="Выберите, что именно Вы планируете",
                         reply_markup=make_inline_keyboard(par=methods_reorg,
                                                           module=module))

    logger.info(f'User : {message.from_user.id}  send: {message.text}')
    await state.set_state(StateClsReorg.processing_state)


@router.callback_query(NumbersCallFactory.filter(F.module == f'{module}_CONF'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Информируем пользователя о перечне документов"""

    btn_pressed = callback.data.split(":")[3]
    await state.update_data(name_reorg=btn_pressed)

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=methods_reorg,
                                                                               key_pressed=btn_pressed,
                                                                               action="pressed"))
    if btn_pressed == "transformation":
        await callback.message.answer(
            text=f'Для формирования запроса на реорганизацию, Вам необходимо предоставить следующие документы:'
                 f'\n⦿ Устав (положение)'
                 f'\n⦿ Документ, подтверждающий полномочия единоличного исполнительного органа'
                 f'\n⦿ Доверенности на участников сделки'
                 f'\n⦿ Согласие на обработку персональных данных'
                 f'\n⦿ Документы, удостоверяющие личность участников сделки'
                 f'\n⦿ Документы, подтверждающие полномочия'
                 f'\n⦿ Протокол / решение о реорганизации')
    else:
        await callback.message.answer(
            text=f'Для формирования запроса на реорганизацию, Вам необходимо предоставить следующие документы:'
                 f'\n⦿ Устав (положение)'
                 f'\n⦿ Документ, подтверждающий полномочия единоличного исполнительного органа'
                 f'\n⦿ Доверенности на участников сделки'
                 f'\n⦿ Согласие на обработку персональных данных'
                 f'\n⦿ Документы, удостоверяющие личность участников сделки'
                 f'\n⦿ Документы, подтверждающие полномочия'
                 f'\n⦿ Протокол / решение о реорганизации'
                 f'\n⦿ Разделительный баланс и передаточный акт')

    logger.info(f'User : {callback.from_user.id}  send: {callback.data}')

    sopd = FSInputFile('./files/СОПД.pdf')
    await callback.message.answer_document(sopd)
    await callback.message.answer(text='Готовы ли Вы сейчас приложить указанные документы?',
                                  reply_markup=make_inline_keyboard_double(par={"Да": "yes", "Нет": "no"},
                                                                           module=module,
                                                                           action="yn"))
    await state.set_state(StateClsReorg.processing_data)


@router.callback_query(NumbersCallFactory.filter(F.value == f'{module}_no'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    logger.info(f'User : {callback.from_user.id}  send: {callback.data}')
    await callback.message.delete_reply_markup()
    await callback.message.answer(text='Когда будете готовы приложить все вышеуказанные документы снова выберите данный тип обращения в Telegram - боте')
    await state.clear()


@router.callback_query(NumbersCallFactory.filter(F.value == f'{module}_yes'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    logger.info(f'User : {callback.from_user.id}  send: {callback.data}')
    await callback.message.delete_reply_markup()
    await callback.message.answer(text="После того, как приложите все документы, нажмите кнопку ниже",
                                  reply_markup=make_inline_keyboard_one(module=module,
                                                                        text="Завершить",
                                                                        action="doc_conf"))

    await state.set_state(StateClsReorg.prepare_data)


@router.callback_query(NumbersCallFactory.filter(F.action == f'{module}_doc_conf'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    logger.info(f'User : {callback.from_user.id}  send: {callback.data}')
    await callback.message.delete_reply_markup()
    await callback.message.answer(text="В случае положительного решения каким образом необходимо направить документы",
                                  reply_markup=make_inline_keyboard(par=methods_feedback, module=f'{module}_END'))

    await state.set_state(StateClsReorg.end_of_script)


@router.message(StateClsReorg.prepare_data)
@logger.catch
async def stage(message: Message, state: FSMContext):
    """Обработка документов пользователя"""

    if document := message.document:
        logger.info(f'User : {message.from_user.id}  document_id: {document.file_id}')
        # await redis.append(key=str(message.from_user.id), value=str(document.file_id))
        # file = await bot.get_file(document.file_id)
        # file_path = file.file_path
        # await bot.download_file(file_path=file_path, destination=f"download_doc/{document.file_name}")
    else:
        await message.answer(text='Неверный формат сообщения')


@router.callback_query(NumbersCallFactory.filter(F.module == f'{module}_END_CONF'))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Завершение обработки документов, формирование заявки"""

    await callback.message.answer(text='Благодарим за обращение!')

    btn_pressed = callback.data.split(":")[3]

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=methods_feedback,
                                                                               key_pressed=btn_pressed,
                                                                               action="pressed"))

    await state.update_data(method_feedback=btn_pressed)
    data = await state.get_data()
    text = f'\nUser : {callback.from_user.id} \nType_reorg: {data["name_reorg"]} \nmethod_feedback : {data["method_feedback"]}'
    logger.success(text)

    await state.clear()
