from aiogram import Router
from aiogram.types import ReplyKeyboardMarkup, Message, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher.filters.command import Command
from aiogram import F
from aiogram.dispatcher.fsm.state import StatesGroup, State
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import FSInputFile

from Keyboards import make_row_keyboard, make_column_keyboard
from loguru import logger



router = Router()


class StateClsReorg(StatesGroup):
    processing_state = State()  # состояние информирования
    processing_data = State()  # состояние предоставления документов
    prepare_data = State()  # состояние обработки документов
    end_of_script = State()  # завершение сценария


methods_reorg = [
    "Слияние",
    "Присоединение",
    "Выделение",
    "Разделение",
    "Преобразование",
    "Другое",
]

methods_feedback = [
    "Данный Telegram бот",
    "ЭДО",
    "Электронная почта"
]


@router.message(Command(commands=["reorg"]))
@logger.catch
async def cmd_start(message: Message, state: FSMContext):
    await message.answer(text="Выберите, что именно Вы планируете",
                         reply_markup=make_column_keyboard(methods_reorg))

    logger.info(f'User : {message.from_user.id}  send: {message.text}')

    await state.set_state(StateClsReorg.processing_state)


@router.message(StateClsReorg.processing_state, F.text.in_(methods_reorg))
@logger.catch
async def stage(message: Message, state: FSMContext):
    """Информируем пользователя о перечне документов"""
    await state.update_data(name_reorg=message.text)
    if message.text == "Преобразование":
        await message.answer(
            text=f'Для формирования запроса на реорганизацию, Вам необходимо предоставить следующие документы:'
                 f'\n⦿ Устав (положение)'
                 f'\n⦿ Документ, подтверждающий полномочия единоличного исполнительного органа'
                 f'\n⦿ Доверенности на участников сделки'
                 f'\n⦿ Согласие на обработку персональных данных'
                 f'\n⦿ Документы, удостоверяющие личность участников сделки'
                 f'\n⦿ Документы, подтверждающие полномочия'
                 f'\n⦿ Протокол / решение о реорганизации')
    else:
        await message.answer(
            text=f'Для формирования запроса на реорганизацию, Вам необходимо предоставить следующие документы:'
                 f'\n⦿ Устав (положение)'
                 f'\n⦿ Документ, подтверждающий полномочия единоличного исполнительного органа'
                 f'\n⦿ Доверенности на участников сделки'
                 f'\n⦿ Согласие на обработку персональных данных'
                 f'\n⦿ Документы, удостоверяющие личность участников сделки'
                 f'\n⦿ Документы, подтверждающие полномочия'
                 f'\n⦿ Протокол / решение о реорганизации'
                 f'\n⦿ Разделительный баланс и передаточный акт')

    logger.info(f'User : {message.from_user.id}  send: {message.text}')

    sopd = FSInputFile('files/СОПД.pdf')
    await message.answer_document(sopd)
    await message.answer(text='Готовы ли Вы сейчас приложить указанные документы?',
                         reply_markup=make_row_keyboard(["Да", "Нет"]))
    await state.set_state(StateClsReorg.processing_data)


@router.message(StateClsReorg.processing_data, F.text.casefold() == "нет")
@logger.catch
async def stage(message: Message, state: FSMContext):
    await message.answer(text='Когда будете готовы приложить все вышеуказанные документы снова выберите данный тип обращения в Telegram - боте')
    await state.clear()


@router.message(StateClsReorg.processing_data, F.text.casefold() == "да")
@logger.catch
async def stage(message: Message, state: FSMContext):
    await message.answer(text="После того, как приложите все документы, введите \"Завершить\"")

    logger.info(f'User : {message.from_user.id}  send: {message.text}')

    await state.set_state(StateClsReorg.prepare_data)


@router.message(StateClsReorg.prepare_data, F.text.casefold() == "завершить")
@logger.catch
async def stage(message: Message, state: FSMContext):
    await message.answer(text="В случае положительного решения каким образом необходимо направить документы",
                         reply_markup=make_column_keyboard(methods_feedback))

    logger.info(f'User : {message.from_user.id}  send: {message.text}')

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


@router.message(StateClsReorg.end_of_script)
@logger.catch
async def stage(message: Message, state: FSMContext):
    """Завершение обработки документов, формирование заявки"""
    await message.answer(text='Благодарим за обращение!')

    # res = await redis.get(name=str(message.from_user.id))
    await state.update_data(method_feedback=message.text)
    data = await state.get_data()
    text = f'\nUser : {message.from_user.id} \nType_reorg: {data["name_reorg"]} \nmethod_feedback : {data["method_feedback"]}'
    logger.success(text)

    await state.clear()
