from aiogram import Router
from aiogram.types import Message
from aiogram.dispatcher.filters.command import Command
from aiogram import F
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram import types
from aiogram.types import FSInputFile
from aiogram.exceptions import TelegramBadRequest
from loguru import logger
from contextlib import suppress
from backend.Keyboards import make_row_keyboard, make_column_keyboard, make_inline_keyboard, replace_keyboard
from backend.Keyboards import NumbersCallFactory

from main import bot

router = Router()


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
    "Включить/исключить франшизу из полиса" : "on/off_franchise"
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
                         reply_markup=make_inline_keyboard(choice_insurance,))
    await state.set_state(StateClsProlongation.processing_state)


@router.callback_query(NumbersCallFactory.filter(F.action == "pressed"))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    pass


@router.callback_query(NumbersCallFactory.filter(F.value == (keyb := list(choice_insurance.values())[1])))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """  ОСАГО  """

    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text=callback.message.text,
                                         reply_markup=replace_keyboard(choice_insurance, keyb, action="hover"))

    logger.info(f'User : {callback.from_user.id}  pressed: {callback.message.text}')
    await state.update_data(choice_insurance=list(choice_insurance.keys())[1])

    # отправка запроса

    await callback.message.answer(text="Благодарим за обращение!")
    await state.clear()


@router.callback_query(NumbersCallFactory.filter(F.value == (keyb2 := list(choice_insurance.values())[0])))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Выбор активности для КАСКО"""

    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text=callback.message.text,
                                         reply_markup=replace_keyboard(choice_insurance, keyb2, action="hover"))

    logger.info(f'User : {callback.from_user.id}  pressed: {keyb2}')
    await state.update_data(choice_insurance=list(choice_insurance.keys())[0])

    await callback.message.answer(text="Что Вам необходимо?",
                                  reply_markup=make_inline_keyboard(choice_action))

    await state.set_state(StateClsProlongation.processing_data)


@router.callback_query(NumbersCallFactory.filter(F.value == (keyb3 := list(choice_action.values())[0])))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Запрос счета на пролонгацию"""

    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text=callback.message.text,
                                         reply_markup=replace_keyboard(choice_action, keyb3, action="hover"))

    logger.info(f'User : {callback.from_user.id}  pressed: {keyb3}')
    await state.update_data(choice_action=list(choice_action.keys())[0])

    # отправка запроса

    await callback.message.answer(text="Благодарим за обращение!")
    await state.clear()


@router.callback_query(NumbersCallFactory.filter(F.value == (keyb4 := list(choice_action.values())[1])))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Смена страховой компании  или  Включить/исключить франшизу из полиса"""

    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text=callback.message.text,
                                         reply_markup=replace_keyboard(choice_action, keyb4, action="hover"))

    logger.info(f'User : {callback.from_user.id}  pressed: {keyb4}')
    await state.update_data(choice_action=list(choice_action.keys())[1])

    await callback.message.answer(text="Сколько дней осталось до пролонгации полиса?",
                                  reply_markup=make_inline_keyboard(choice_time))

    await state.set_state(StateClsProlongation.prepare_data)


@router.callback_query(NumbersCallFactory.filter(F.value == (keyb5 := list(choice_time.values())[0])))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Если более 20 рабочих дней"""

    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text=callback.message.text,
                                      reply_markup=replace_keyboard(choice_time, keyb5, action="hover"))

    logger.info(f'User : {callback.message.from_user.id}  send: {keyb5}')
    await state.update_data(choice_action=list(choice_time.keys())[0])

    # отправка запроса

    await callback.message.answer(text="Благодарим за обращение!")
    await state.clear()


@router.callback_query(NumbersCallFactory.filter(F.value == (keyb6 := list(choice_time.values())[1])))
@logger.catch
async def stage(callback: types.CallbackQuery, state: FSMContext):
    """Если менее 20 рабочих дней"""

    with suppress(TelegramBadRequest):
        await callback.message.edit_text(text=callback.message.text,
                                         reply_markup=replace_keyboard(choice_time, keyb6, action="hover"))

    logger.info(f'User : {callback.message.from_user.id}  send: {keyb6}')
    await callback.message.answer(text=f'Уважаемый клиент, добрый день!'
        f'\nВ соответствии с п. 1.11 Договора лизинга, страхование осуществляется в соответствии с разделом 5 общих условий.'
        f'\nСогласно пункту  5.19. общих условий,  В случае намерения Лизингополучателя заменить Страховщика и/или изменить цели '
        f'эксплуатации Предмета лизинга, списка лиц, допущенных к управлению Предмета лизинга, иных параметров, влияющих на '
        f'страхование Предмета лизинга, заявленных изначально, Лизингополучатель обязан за 20 (двадцать) рабочих дней до даты пролонгации.')
    await state.clear()


@router.message()
@logger.catch
async def stage(message: Message, state: FSMContext):
    logger.debug(f'User : {message.from_user.id}  send: {message.text}')
    await message.answer(text='Я такого не умею(')



