from aiogram import Router
from aiogram.types import Message
from aiogram.dispatcher.filters.command import Command
from aiogram import F
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from loguru import logger
from contextlib import suppress
from backend.Keyboards import make_inline_keyboard, replace_keyboard
from backend.Keyboards import NumbersCallFactory


router = Router()
module = "Prolongation"

class StateClsProlongation(StatesGroup):
    processing_state = State()  # состояние информирования
    processing_data = State()  # состояние предоставления документов
    prepare_data = State()  # состояние обработки документов
    end_of_script = State()  # завершение сценария


choice_insurance = {
    "Получение полиса КАСКО" : "get_kasko",
    "Получение полиса ОСАГО" : "get_osago"
}

choice_action = {
    "Счет на пролонгацию" : "check_prolong",
    "Сменить страховую компанию" : "change_company",
    "Включить/исключить франшизу из полиса" : "franchise"
}

choice_time = {
    "Более 20 рабочих дней" : "more_20",
    "Менее 20 рабочих дней" : "less_20"
}


@router.message(Command(commands=["prng"]))
@logger.catch
async def cmd_start(message: Message, state: FSMContext):
    logger.info(f'User : {message.from_user.id}  send: {message.text}')
    await message.answer(text="Какой полис Вы хотите пролонгировать?",
                         reply_markup=make_inline_keyboard(par=choice_insurance, module=module))
    await state.set_state(StateClsProlongation.processing_state)


@router.callback_query(NumbersCallFactory.filter(F.action == "get_osago"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """  ОСАГО  """

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=choice_insurance,
                                                                               key_pressed="get_osago",
                                                                               action="pressed"))

    logger.info(f'User : {callback.from_user.id}  pressed: {callback.data}')
    await state.update_data(choice_insurance="get_osago")

    # отправка запроса

    await callback.message.answer(text="Благодарим за обращение!")
    await state.clear()


@router.callback_query(NumbersCallFactory.filter(F.action == "get_kasko"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Выбор активности для КАСКО"""

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=choice_insurance,
                                                                               key_pressed="get_kasko",
                                                                               action="pressed"))

    logger.info(f'User : {callback.from_user.id}  pressed: {callback.data}')
    await state.update_data(choice_insurance="get_kasko")

    await callback.message.answer(text="Что Вам необходимо?",
                                  reply_markup=make_inline_keyboard(par=choice_action, module=module))

    await state.set_state(StateClsProlongation.processing_data)


@router.callback_query(NumbersCallFactory.filter(F.action == "check_prolong"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Запрос счета на пролонгацию"""

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=choice_action,
                                                                               key_pressed="check_prolong",
                                                                               action="pressed"))

    logger.info(f'User : {callback.from_user.id}  pressed: {callback.data}')
    await state.update_data(choice_action="check_prolong")

    # отправка запроса

    await callback.message.answer(text="Благодарим за обращение!")
    await state.clear()


@router.callback_query(NumbersCallFactory.filter(F.action == "change_company"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Смена страховой компании"""

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=choice_action,
                                                                               key_pressed="change_company",
                                                                               action="pressed"))

    logger.info(f'User : {callback.from_user.id}  pressed: {callback.data}')
    await state.update_data(choice_action="change_company")

    await callback.message.answer(text="Сколько дней осталось до пролонгации полиса?",
                                  reply_markup=make_inline_keyboard(par=choice_time, module=module))

    await state.set_state(StateClsProlongation.prepare_data)


@router.callback_query(NumbersCallFactory.filter(F.action == "franchise"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Включить/исключить франшизу из полиса"""

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=choice_action,
                                                                               key_pressed="franchise",
                                                                               action="pressed"))

    logger.info(f'User : {callback.from_user.id}  pressed: {callback.data}')
    await state.update_data(choice_action="franchise")

    await callback.message.answer(text="Сколько дней осталось до пролонгации полиса?",
                                  reply_markup=make_inline_keyboard(par=choice_time, module=module))

    await state.set_state(StateClsProlongation.prepare_data)


@router.callback_query(NumbersCallFactory.filter(F.action == "more_20"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Если более 20 рабочих дней"""

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=choice_time,
                                                                               key_pressed="more_20",
                                                                               action="pressed"))

    logger.info(f'User : {callback.from_user.id}  pressed: {callback.data}')
    await state.update_data(choice_time="more_20")

    # отправка запроса

    await callback.message.answer(text="Благодарим за обращение!")
    await state.clear()


@router.callback_query(NumbersCallFactory.filter(F.action == "less_20"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Если менее 20 рабочих дней"""

    with suppress(TelegramBadRequest):
        await callback.message.edit_reply_markup(reply_markup=replace_keyboard(module=module,
                                                                               keyboard=choice_time,
                                                                               key_pressed="less_20",
                                                                               action="pressed"))

    logger.info(f'User : {callback.from_user.id}  pressed: {callback.data}')

    await callback.message.answer(text=f'Уважаемый клиент, добрый день!'
        f'\nВ соответствии с п. 1.11 Договора лизинга, страхование осуществляется в соответствии с разделом 5 общих условий.'
        f'\nСогласно пункту  5.19. общих условий,  В случае намерения Лизингополучателя заменить Страховщика и/или изменить цели '
        f'эксплуатации Предмета лизинга, списка лиц, допущенных к управлению Предмета лизинга, иных параметров, влияющих на '
        f'страхование Предмета лизинга, заявленных изначально, Лизингополучатель обязан за 20 (двадцать) рабочих дней до даты пролонгации.')
    await state.clear()

