from aiogram import Router
from aiogram.types import Message
from aiogram.dispatcher.filters.command import Command
from aiogram import F
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import FSInputFile

from backend.Keyboards import make_row_keyboard, make_column_keyboard
from loguru import logger


router = Router()


class StateClsProlongation(StatesGroup):
    processing_state = State()  # состояние информирования
    processing_data = State()  # состояние предоставления документов
    prepare_data = State()  # состояние обработки документов
    end_of_script = State()  # завершение сценария


choice_insurance = [
    "Получение полиса КАСКО",
    "Получение полиса ОСАГО"
]

choice_action = [
    "Счет на пролонгацию",
    "Сменить страховую компанию",
    "Включить/исключить франшизу из полиса"
]

choice_time = [
    "Более 20 рабочих дней",
    "Менее 20 рабочих дней"
]


@router.message(Command(commands=["prng"]))
@logger.catch
async def cmd_start(message: Message, state: FSMContext):
    logger.info(f'User : {message.from_user.id}  send: {message.text}')
    await message.answer(text="Какой полис Вы хотите пролонгировать?",
                         reply_markup=make_column_keyboard(choice_insurance))

    await state.set_state(StateClsProlongation.processing_state)


@router.message(StateClsProlongation.processing_state, F.text.in_(choice_insurance[1]))
@logger.catch
async def stage(message: Message, state: FSMContext):
    """  ОСАГО  """
    logger.info(f'User : {message.from_user.id}  send: {message.text}')
    await state.update_data(choice_insurance=message.text)

    # Отправка данных по обращению

    await message.answer(text="Благодарим за обращение!")
    await state.clear()


@router.message(StateClsProlongation.processing_state, F.text.in_(choice_insurance[0]))
@logger.catch
async def stage(message: Message, state: FSMContext):
    """Выбор активности для КАСКО"""

    await state.update_data(choice_insurance=message.text)
    await message.answer(text="Что Вам необходимо?",
                         reply_markup=make_column_keyboard(choice_action))

    logger.info(f'User : {message.from_user.id}  send: {message.text}')

    await state.set_state(StateClsProlongation.processing_data)


@router.message(StateClsProlongation.processing_data, F.text.in_(choice_action[0]))
@logger.catch
async def stage(message: Message, state: FSMContext):
    """Запрос счета на пролонгацию"""

    # Отправка данных по обращению

    await message.answer(text="Благодарим за обращение!")
    await state.clear()


@router.message(StateClsProlongation.processing_data, F.text.in_(choice_action[1]) | F.text.in_(choice_action[2]))
@logger.catch
async def stage(message: Message, state: FSMContext):
    """Смена страховой компании  или  Включить/исключить франшизу из полиса"""

    await message.answer(text="Сколько дней осталось до пролонгации полиса?",
                         reply_markup=make_column_keyboard(choice_time))

    await state.set_state(StateClsProlongation.prepare_data)


@router.message(StateClsProlongation.prepare_data, F.text.in_(choice_time[0]))
@logger.catch
async def stage(message: Message, state: FSMContext):
    """Если более 20 рабочих дней"""

    # Отправка данных по обращению

    await message.answer(text="Благодарим за обращение!")
    await state.clear()


@router.message(StateClsProlongation.prepare_data, F.text.in_(choice_time[1]))
@logger.catch
async def stage(message: Message, state: FSMContext):
    """Если менее 20 рабочих дней"""

    await message.answer(text=f'Уважаемый клиент, добрый день!'
        f'\nВ соответствии с п. 1.11 Договора лизинга, страхование осуществляется в соответствии с разделом 5 общих условий.' 
        f'\nСогласно пункту  5.19. общих условий,  В случае намерения Лизингополучателя заменить Страховщика и/или изменить цели ' 
        f'эксплуатации Предмета лизинга, списка лиц, допущенных к управлению Предмета лизинга, иных параметров, влияющих на ' 
        f'страхование Предмета лизинга, заявленных изначально, Лизингополучатель обязан за 20 (двадцать) рабочих дней до даты пролонгации.')
    await state.clear()


@router.message()
@logger.catch
async def stage(message: Message, state: FSMContext):
    await message.answer(text='Я такого не умею(')

